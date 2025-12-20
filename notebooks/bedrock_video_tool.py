"""
Bedrock Video Analysis Tool for Strands Agents

Uses AWS Bedrock Pegasus model for video analysis.
Automatically uploads local files to S3 if needed.
"""

import os
import json
import boto3
from typing import Dict
from strands import tool

@tool
def bedrock_video_analysis(
    action: str,
    video_path: str = None,
    prompt: str = None,
    bucket_name: str = None,
    video_filter: str = None,
    temperature: float = 0.2
) -> Dict:
    """
    Video analysis using AWS Bedrock Pegasus model.
    
    Actions:
    - analyze: Analyze video with prompt (video_path=file/S3_URI, prompt=question)
    - search_bucket: Search for videos in S3 bucket
    - list_videos: List videos in S3 bucket
    
    Args:
        action: Operation (analyze/search_bucket/list_videos)
        video_path: Local file path or S3 URI
        prompt: Question to ask about video
        bucket_name: S3 bucket name
        video_filter: Filter pattern for search
        temperature: Model temperature
        
    Returns:
        Dict with operation results
    """
    
    if action == "analyze":
        if not video_path or not prompt:
            return {"status": "error", "content": [{"text": "video_path and prompt are required"}]}
        
        try:
            aws_region = os.environ.get('AWS_REGION', 'us-east-1')
            bedrock = boto3.client("bedrock-runtime", region_name=aws_region)
            sts = boto3.client("sts", region_name=aws_region)
            
            # Handle local file upload to S3
            if not video_path.startswith("s3://"):
                if not os.path.exists(video_path):
                    return {"status": "error", "content": [{"text": f"Video file not found: {video_path}"}]}
                
                if not bucket_name:
                    bucket_name = os.environ.get('S3_BUCKET_NAME', 'strands-agents-samples')
                
                # Upload to S3
                s3_client = boto3.client('s3', region_name=aws_region)
                
                # Create bucket if needed
                try:
                    s3_client.head_bucket(Bucket=bucket_name)
                except:
                    try:
                        if aws_region == 'us-east-1':
                            s3_client.create_bucket(Bucket=bucket_name)
                        else:
                            s3_client.create_bucket(
                                Bucket=bucket_name,
                                CreateBucketConfiguration={'LocationConstraint': aws_region}
                            )
                    except:
                        pass
                
                # Upload file
                filename = os.path.basename(video_path)
                s3_key = f"videos/{filename}"
                s3_client.upload_file(video_path, bucket_name, s3_key)
                video_path = f"s3://{bucket_name}/{s3_key}"
            
            # Call Bedrock
            account_id = sts.get_caller_identity()["Account"]
            
            body = {
                "inputPrompt": prompt,
                "mediaSource": {
                    "s3Location": {
                        "uri": video_path,
                        "bucketOwner": account_id
                    }
                },
                "temperature": temperature
            }
            
            response = bedrock.invoke_model(
                modelId="twelvelabs.pegasus-1-2-v1:0",
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            
            return {
                "status": "success",
                "content": [{
                    "json": {
                        "video_path": video_path,
                        "prompt": prompt,
                        "response": response_body.get("message", "No response"),
                        "finish_reason": response_body.get("finishReason", "unknown")
                    }
                }]
            }
            
        except Exception as e:
            return {"status": "error", "content": [{"text": f"Bedrock analysis failed: {str(e)}"}]}
    
    elif action in ["search_bucket", "list_videos"]:
        if not bucket_name:
            bucket_name = os.environ.get('S3_BUCKET_NAME')
            if not bucket_name:
                return {"status": "error", "content": [{"text": "bucket_name parameter or S3_BUCKET_NAME environment variable required"}]}
        
        try:
            aws_region = os.environ.get('AWS_REGION', 'us-east-1')
            s3 = boto3.client("s3", region_name=aws_region)
            
            response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=100)
            
            # Filter for video files
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v']
            objects = response.get("Contents", [])
            
            videos = []
            for obj in objects:
                key = obj["Key"]
                if any(key.lower().endswith(ext) for ext in video_extensions):
                    if not video_filter or video_filter.lower() in key.lower():
                        videos.append({
                            "key": key,
                            "size": obj["Size"],
                            "last_modified": obj["LastModified"].isoformat(),
                            "s3_uri": f"s3://{bucket_name}/{key}"
                        })
            
            return {
                "status": "success",
                "content": [{
                    "json": {
                        "bucket": bucket_name,
                        "videos": videos,
                        "total_count": len(videos),
                        "filter_applied": video_filter or "none"
                    }
                }]
            }
            
        except Exception as e:
            return {"status": "error", "content": [{"text": f"Failed to search bucket: {str(e)}"}]}
    
    else:
        return {"status": "error", "content": [{"text": f"Invalid action: {action}. Use analyze, search_bucket, or list_videos"}]}
