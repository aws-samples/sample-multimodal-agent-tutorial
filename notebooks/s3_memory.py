"""
S3 Vector Memory Tool for Strands Agents

AWS-native memory management using Amazon S3 Vectors with automatic user isolation.
Provides persistent memory storage and retrieval for Strands agents.

Features:
    - ✅ Automatic vector bucket creation if it doesn't exist
    - ✅ Automatic index creation with optimal configuration
    - ✅ User-isolated memory storage
    - ✅ Semantic search across memories
    - ✅ Production-ready infrastructure

Usage:
    from strands import Agent
    from s3_memory import s3_vector_memory

    agent = Agent(tools=[s3_vector_memory])

    # Store a memory (bucket and index created automatically on first use)
    agent.tool.s3_vector_memory(
        action="store",
        content="User prefers vegetarian food",
        user_id="user123"
    )

    # Retrieve relevant memories
    agent.tool.s3_vector_memory(
        action="retrieve",
        query="food preferences",
        user_id="user123",
        top_k=5
    )

    # List all memories
    agent.tool.s3_vector_memory(
        action="list",
        user_id="user123"
    )

Environment Variables:
    VECTOR_BUCKET_NAME: S3 Vector bucket name (default: multimodal-vector-store)
    VECTOR_INDEX_NAME: Vector index name (default: strands-multimodal)
    AWS_REGION: AWS region (default: us-east-1)
    EMBEDDING_MODEL: Amazon Nova Multimodal Embeddings
        - amazon.nova-2-multimodal-embeddings-v1:0 (1024 dims, supports text/image/video/audio)

Requirements:
    - AWS credentials configured
    - Amazon S3 Vectors service access
    - Amazon Bedrock access for embeddings
    - IAM permissions for s3vectors:* and bedrock:InvokeModel
"""

import boto3
import json
import uuid
import os
import time
from typing import Dict, List
from datetime import datetime
from strands import tool

@tool
def s3_vector_memory(
    action: str,
    content: str = None,
    query: str = None,
    user_id: str = None,
    vector_bucket_name: str = None,
    index_name: str = None,
    top_k: int = 20,
    region_name: str = None,
    embedding_model: str = None,
    min_score: float = 0.1
) -> Dict:
    """
    AWS-native memory management using Amazon S3 Vectors.
    
    Actions:
    - store: Store new memory content
    - retrieve: Search and retrieve relevant memories
    - list: List all user memories
    
    Args:
        action: Operation to perform (store/retrieve/list)
        content: Content to store (required for store action)
        query: Search query (required for retrieve action)
        user_id: User identifier for memory isolation (required)
        vector_bucket_name: S3 Vector bucket (env: VECTOR_BUCKET_NAME)
        index_name: Vector index name (env: VECTOR_INDEX_NAME)
        top_k: Maximum results to return (default: 20)
        region_name: AWS region (env: AWS_REGION, default: us-east-1)
        embedding_model: Bedrock embedding model (env: EMBEDDING_MODEL)
        min_score: Minimum similarity threshold (default: 0.1)
        
    Returns:
        Dict with operation results and status
    """
    
    # Validate required user_id for security
    if not user_id:
        return {"status": "error", "message": "user_id is required for memory isolation"}
    
    try:
        # Load configuration from environment or parameters
        config = {
            "bucket_name": vector_bucket_name or os.environ.get('VECTOR_BUCKET_NAME', 'multimodal-vector-store'),
            "index_name": index_name or os.environ.get('VECTOR_INDEX_NAME', 'strands-multimodal'),
            "region": region_name or os.environ.get('AWS_REGION', 'us-east-1'),
            "model_id": embedding_model or os.environ.get('EMBEDDING_MODEL', 'amazon.nova-2-multimodal-embeddings-v1:0')
        }
        
        # Initialize AWS clients
        bedrock = boto3.client("bedrock-runtime", region_name=config["region"])
        s3vectors = boto3.client("s3vectors", region_name=config["region"])
        
        # Ensure vector store infrastructure exists
        _ensure_vector_store_exists(s3vectors, config)
        
        # Route to appropriate action
        if action == "store":
            return _store_memory(s3vectors, bedrock, config, content, user_id)
        elif action == "retrieve":
            return _retrieve_memories(s3vectors, bedrock, config, query, user_id, top_k, min_score)
        elif action == "list":
            return _list_memories(s3vectors, bedrock, config, user_id, top_k)
        else:
            return {"status": "error", "message": f"Invalid action: {action}"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _ensure_vector_store_exists(s3vectors, config):
    """
    Ensure S3 Vector Store bucket and index exist, create if they don't.
    
    Args:
        s3vectors: boto3 s3vectors client
        config: Configuration dictionary with bucket_name, index_name, region
    """
    try:
        # Check if vector bucket exists
        try:
            s3vectors.get_vector_bucket(vectorBucketName=config["bucket_name"])
            print(f"✅ Vector bucket '{config['bucket_name']}' already exists")
        except Exception as e:
            if "NotFoundException" in str(e) or "NoSuchBucket" in str(e):
                # Create vector bucket
                print(f"📦 Creating vector bucket '{config['bucket_name']}'...")
                s3vectors.create_vector_bucket(
                    vectorBucketName=config["bucket_name"]
                )
                print(f"✅ Vector bucket '{config['bucket_name']}' created successfully")
            else:
                raise
        
        # Check if index exists
        try:
            index_info = s3vectors.get_index(
                vectorBucketName=config["bucket_name"],
                indexName=config["index_name"]
            )
            print(f"✅ Index '{config['index_name']}' already exists")
        except Exception as e:
            if "NotFoundException" in str(e):
                # Create index with appropriate dimensions for embeddings
                print(f"📊 Creating index '{config['index_name']}'...")
                s3vectors.create_index(
                    vectorBucketName=config["bucket_name"],
                    indexName=config["index_name"],
                    dataType="float32",
                    dimension=1024,  # Compatible with Nova and Titan (1024 dims)
                    distanceMetric="cosine",
                    metadataConfiguration={
                        # Non-filterable keys: content and timestamp (we only filter by user_id)
                        "nonFilterableMetadataKeys": ["content", "timestamp"]
                    }
                )
                print(f"✅ Index '{config['index_name']}' created and ready!")
                
                # Verify index was created successfully
                try:
                    index_info = s3vectors.get_index(
                        vectorBucketName=config["bucket_name"],
                        indexName=config["index_name"]
                    )
                    print(f"   Dimension: {index_info['index']['dimension']}, Metric: {index_info['index']['distanceMetric']}")
                except Exception as verify_error:
                    print(f"⚠️ Could not verify index: {str(verify_error)}")
            else:
                raise
            
    except Exception as e:
        print(f"⚠️ Warning during vector store setup: {str(e)}")
        # Don't fail the entire operation, let it proceed and fail later if needed

def _generate_embedding(bedrock, model_id: str, text: str, embedding_purpose: str = "GENERIC_INDEX") -> List[float]:
    """
    Generate text embedding using Amazon Nova Multimodal Embeddings.
    
    Args:
        bedrock: Bedrock runtime client
        model_id: Model identifier (amazon.nova-2-multimodal-embeddings-v1:0)
        text: Text to embed
        embedding_purpose: Purpose (GENERIC_INDEX for storing, GENERIC_RETRIEVAL for querying)
    
    Returns:
        List of floats representing the embedding (1024 dimensions)
    """
    # Truncate text if exceeds model limit (8K tokens)
    if len(text) > 8000:
        text = text[:8000]
    
    # Amazon Nova Multimodal Embeddings API
    request_body = {
        "taskType": "SINGLE_EMBEDDING",
        "singleEmbeddingParams": {
            "embeddingPurpose": embedding_purpose,
            "embeddingDimension": 1024,  # 1024 dims for optimal performance
            "text": {"truncationMode": "END", "value": text}
        }
    }
    
    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body),
        contentType="application/json"
    )
    
    response_body = json.loads(response["body"].read())
    return response_body["embeddings"][0]["embedding"]

def _store_memory(s3vectors, bedrock, config, content, user_id):
    """Store memory with user isolation."""
    if not content:
        return {"status": "error", "message": "content is required for store action"}
    
    # Generate embedding for indexing
    embedding = _generate_embedding(bedrock, config["model_id"], content, embedding_purpose="GENERIC_INDEX")
    
    # Create unique memory key with user prefix
    memory_key = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Prepare vector data with metadata
    vector_data = {
        "key": memory_key,
        "data": {"float32": [float(x) for x in embedding]},
        "metadata": {
            "user_id": user_id,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # Store in S3 Vectors
    s3vectors.put_vectors(
        vectorBucketName=config["bucket_name"],
        indexName=config["index_name"],
        vectors=[vector_data]
    )
    
    return {
        "status": "success", 
        "message": "Memory stored successfully", 
        "memory_key": memory_key
    }

def _retrieve_memories(s3vectors, bedrock, config, query, user_id, top_k, min_score):
    """Retrieve relevant memories for user."""
    if not query:
        return {"status": "error", "message": "query is required for retrieve action"}
    
    # Generate query embedding for retrieval
    query_embedding = _generate_embedding(bedrock, config["model_id"], query, embedding_purpose="GENERIC_RETRIEVAL")
    
    # Search with user filter for isolation
    response = s3vectors.query_vectors(
        vectorBucketName=config["bucket_name"],
        indexName=config["index_name"],
        queryVector={"float32": query_embedding},
        topK=top_k,
        filter={"user_id": user_id},
        returnDistance=True,
        returnMetadata=True
    )
    
    # Process results
    memories = []
    for vector in response.get("vectors", []):
        # Verify user isolation
        if vector["metadata"].get("user_id") != user_id:
            continue
            
        # Calculate similarity score
        similarity = 1.0 - vector.get("distance", 1.0)
        
        # Filter by minimum score
        if similarity >= min_score:
            memories.append({
                "id": vector["key"],
                "memory": vector["metadata"].get("content", ""),
                "similarity": round(similarity, 3),
                "created_at": vector["metadata"].get("timestamp", "")
            })
    
    # Sort by similarity
    memories.sort(key=lambda x: x["similarity"], reverse=True)
    
    return {
        "status": "success",
        "memories": memories[:top_k],
        "total_found": len(memories),
        "query": query
    }

def _list_memories(s3vectors, bedrock, config, user_id, top_k):
    """List all user memories."""
    # Use generic embedding for listing
    generic_embedding = _generate_embedding(bedrock, config["model_id"], "user memories", embedding_purpose="GENERIC_RETRIEVAL")
    
    # Query all user vectors
    response = s3vectors.query_vectors(
        vectorBucketName=config["bucket_name"],
        indexName=config["index_name"],
        queryVector={"float32": generic_embedding},
        topK=top_k,
        filter={"user_id": user_id},
        returnMetadata=True
    )
    
    # Process memories
    memories = []
    for vector in response.get("vectors", []):
        # Verify user isolation
        if vector["metadata"].get("user_id") != user_id:
            continue
            
        memories.append({
            "id": vector["key"],
            "memory": vector["metadata"].get("content", ""),
            "created_at": vector["metadata"].get("timestamp", "")
        })
    
    # Sort by creation time
    memories.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return {
        "status": "success", 
        "memories": memories, 
        "total_found": len(memories)
    }
