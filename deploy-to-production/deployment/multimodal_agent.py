from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands_tools import image_reader,file_read
from video_reader_local import video_reader_local
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
import base64
import tempfile
import os


system_prompt = """
You are an expert AI travel assistant with persistent memory.

Your capabilities:
- **Personalized Recommendations**: Tailor suggestions based on user preferences
- **Multimodal Analysis**: Process photos, videos, documents, and text
- **Cross-Session Memory**: Remember preferences and context from previous conversations
- **Cultural Expertise**: Provide insights about destinations, cuisine, and local experiences

Available Tools:
1. **image_reader**: Use this to analyze images (food, destinations, landmarks, menus, etc.)
   - When you see a file path in the user's message, use this tool to read and analyze the image
   - Example: "Use the image_reader tool to read the image at: /tmp/image.jpg"

2. **video_reader_local**: Use this to analyze videos (travel vlogs, destination tours, cultural experiences)
   - When you see a video file path, use this tool to analyze the video content
   - Note: Videos are visual only (no audio analysis)
   - Example: "Use the video_reader_local tool to analyze the video at: /tmp/video.mp4"

3. **file_read**: Use this to read text documents (itineraries, PDFs, travel guides)
   - When you need to read document content

Memory Usage Guidelines:
1. **Always start** by retrieving relevant memories about the user
2. **Store important information**:
   - Travel preferences (food, activities, accommodation style)
   - Dietary restrictions or requirements
   - Budget considerations
   - Destinations of interest
   - Past travel experiences
   - Visual preferences from analyzed images/videos
3. **Build context** over multiple interactions
4. **Reference previous conversations** when relevant

When analyzing multimodal content:
1. Retrieve user's travel preferences from memory
2. Use the appropriate tool (image_reader, video_reader_local, or file_read)
3. Analyze the content in detail
4. Store key insights and visual details in memory
5. Provide personalized recommendations based on both the content and stored preferences

Always be enthusiastic, helpful, and culturally sensitive.
"""

app = BedrockAgentCoreApp()

MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID")
REGION = os.getenv("AWS_REGION", "us-east-1")

# Global agent instance
_agent = None

def get_or_create_agent(actor_id: str, session_id: str) -> Agent:
    """
    Get existing agent or create new one with memory configuration.
    Since the container is pinned to the session ID, we only need one agent per container.
    """
    global _agent
    
    if _agent is None:
        # Configure memory if available
        session_manager = None
        if MEMORY_ID:
            memory_config = AgentCoreMemoryConfig(
                memory_id=MEMORY_ID,
                session_id=session_id,
                actor_id=actor_id,
                retrieval_config={
                    f"/users/{actor_id}/facts": RetrievalConfig(top_k=3, relevance_score=0.5),
                    f"/users/{actor_id}/preferences": RetrievalConfig(top_k=3, relevance_score=0.5)
                }
            )
            session_manager = AgentCoreMemorySessionManager(memory_config, REGION)
        
        # Create agent with or without memory
        _agent = Agent(
            model=BedrockModel(model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0"),
            tools=[image_reader, file_read,video_reader_local],
            system_prompt=system_prompt,
            session_manager=session_manager
        )
    
    return _agent

@app.entrypoint
def invoke(payload, context=None):
    """Handle multimodal requests with text and images"""
    user_message = payload.get("prompt", "")
    
    # Validate prompt is not empty and has meaningful content
    if not user_message or not user_message.strip():
        return {"result": "Error: No message provided"}
    
    # Ensure message has actual text content
    user_message = user_message.strip()
    if len(user_message) == 0:
        return {"result": "Error: Empty message content"}
    
    # Extract session and actor information
    actor_id = 'whatsapp-user'
    session_id = 'whatsapp-session'
    
    if context and hasattr(context, 'request_headers') and context.request_headers:
        actor_id = context.request_headers.get('X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actor-Id', 'whatsapp-user')
        session_id = context.session_id or 'whatsapp-session'
    
    # Get or create agent with proper session management
    agent = get_or_create_agent(actor_id, session_id)
    
    # Handle media data if present (images or videos)
    if "media" in payload:
        media = payload["media"]
        media_type = media.get("type")
        
        if media_type == "image":
            # Decode base64 image and save temporarily
            image_data = base64.b64decode(media["data"])
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{media.get("format", "jpg")}') as tmp_file:
                tmp_file.write(image_data)
                tmp_file.flush()  # Ensure data is written to disk
                media_path = tmp_file.name
            
            try:
                # Ensure we have meaningful text with the image
                if user_message.lower().strip() in ["", "image", "analyze", "check"]:
                    prompt = f"I'm sharing an image with you. Please analyze it and provide travel recommendations. Use the image_reader tool to read the image at: {media_path}"
                else:
                    prompt = f"{user_message}. Use the image_reader tool to read the image at: {media_path}"
                
                result = agent(prompt)
                
                # Handle response correctly based on AgentCore pattern
                if hasattr(result, 'message') and result.message:
                    if isinstance(result.message, dict) and 'content' in result.message:
                        # Extract text from content array
                        content = result.message.get('content', [{}])
                        if content and len(content) > 0:
                            response_text = content[0].get('text', str(result))
                        else:
                            response_text = str(result)
                    else:
                        response_text = str(result.message)
                else:
                    response_text = str(result)
                
                return {"result": response_text}
            finally:
                # Clean up temp file
                os.unlink(media_path)
        
        elif media_type == "video":
            # Decode base64 video and save temporarily
            video_data = base64.b64decode(media["data"])
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{media.get("format", "mp4")}') as tmp_file:
                tmp_file.write(video_data)
                tmp_file.flush()  # Ensure data is written to disk
                media_path = tmp_file.name
            
            try:
                # Ensure we have meaningful text with the video
                if user_message.lower().strip() in ["", "video", "analyze", "check"]:
                    prompt = f"I'm sharing a travel video with you. Please analyze it and provide recommendations. Use the video_reader_local tool to analyze the video at: {media_path}"
                else:
                    prompt = f"{user_message}. Use the video_reader_local tool to analyze the video at: {media_path}"
                
                result = agent(prompt)
                
                # Handle response correctly based on AgentCore pattern
                if hasattr(result, 'message') and result.message:
                    if isinstance(result.message, dict) and 'content' in result.message:
                        # Extract text from content array
                        content = result.message.get('content', [{}])
                        if content and len(content) > 0:
                            response_text = content[0].get('text', str(result))
                        else:
                            response_text = str(result)
                    else:
                        response_text = str(result.message)
                else:
                    response_text = str(result)
                
                return {"result": response_text}
            finally:
                # Clean up temp file
                os.unlink(media_path)
    
    # Text-only processing - ensure we have meaningful content
    if len(user_message) < 3:  # Very short messages might cause issues
        user_message = f"Please help me with: {user_message}"
    
    result = agent(user_message)
    
    # Handle response correctly based on AgentCore pattern
    if hasattr(result, 'message') and result.message:
        if isinstance(result.message, dict) and 'content' in result.message:
            # Extract text from content array
            content = result.message.get('content', [{}])
            if content and len(content) > 0:
                response_text = content[0].get('text', str(result))
            else:
                response_text = str(result)
        else:
            response_text = str(result.message)
    else:
        response_text = str(result)
    
    return {"result": response_text}

def lambda_handler(event, context):
    """AWS Lambda handler"""
    return app.lambda_handler(event, context)

if __name__ == "__main__":
    app.run()
