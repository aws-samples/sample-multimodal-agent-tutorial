"""
Video Reader Tool for Strands Agents
"""
import boto3
import os
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
from strands import tool

@tool
def video_reader(
    video_path: str, 
    text_prompt: str = "Describe what you see in this video",
    model_id: str = "us.amazon.nova-pro-v1:0",
    region: Optional[str] = None,
    s3_bucket: Optional[str] = None,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze video content using AWS Bedrock's multimodal capabilities.
    
    This tool processes videos and uses Nova/Claude models to analyze video content 
    through Bedrock's Converse API.
    
    IMPORTANT MODEL LIMITATIONS (Amazon Nova):
    For complete details see: https://docs.aws.amazon.com/nova/latest/userguide/prompting-vision-limitations.html
    
    - Only 1 video per request supported
    - No audio analysis (visual content only)
    - Limited temporal causality understanding
    - Cannot identify or name people in videos
    - Limited spatial reasoning capabilities
    - May struggle with small text in videos
    - Approximate counting only (not precise for large numbers)
    - Will not process inappropriate/explicit content
    - Not suitable for medical diagnostic purposes
    
    Args:
        video_path: Path to video file (local path or S3 URI like s3://bucket/video.mp4)
        text_prompt: Question or instruction for analyzing the video
        model_id: Bedrock model ID to use for analysis
        region: AWS region for Bedrock client
        s3_bucket: S3 bucket name for uploading local videos
        system_prompt: Custom system prompt for analysis
        
    Returns:
        Dictionary with video analysis results
    """
    # Validate Nova model limitations
    if "identify" in text_prompt.lower() or "who is" in text_prompt.lower():
        return {
            "status": "error",
            "content": [{"text": "❌ Nova models cannot identify or name people in videos"}]
        }
    
    try:
        # Get defaults from environment if not provided
        if not region:
            region = os.getenv('AWS_REGION', 'us-east-1')
        
        if not system_prompt:
            system_prompt = "Always answer in the same language you are asked. Note: I can only analyze visual content, not audio."
        
        # Initialize Bedrock client
        session = boto3.Session(region_name=region)
        bedrock_client = session.client('bedrock-runtime')
        
        # Determine video format
        video_format = _get_video_format(video_path)
        if not video_format:
            return {
                "status": "error",
                "content": [{"text": "❌ Unsupported video format. Supported: mp4, mov, avi, mkv, webm"}]
            }
        
        # Handle S3 URI or upload local file
        if video_path.startswith('s3://'):
            s3_uri = video_path
        else:
            # Upload local file to S3
            if not s3_bucket:
                s3_bucket = os.getenv('VIDEO_READER_S3_BUCKET', 'strands-agents-samples')
            
            s3_uri = _upload_to_s3(video_path, s3_bucket, session)
            if not s3_uri:
                return {
                    "status": "error", 
                    "content": [{"text": "❌ Failed to upload video to S3"}]
                }
        
        # Prepare message for Converse API
        media_content = {
            'video': {
                "format": video_format,
                "source": {
                    's3Location': {
                        'uri': s3_uri
                    }
                }
            }
        }
        
        message = {
            "role": "user",
            "content": [
                {"text": text_prompt},
                media_content
            ]
        }
        
        # Call Bedrock Converse API
        response = bedrock_client.converse(
            modelId=model_id,
            messages=[message],
            system=[{"text": system_prompt}]
        )
        
        # Extract response content
        text_response = response['output']['message']['content'][0]['text']
        
        # Format detailed response with metadata in the text content
        detailed_response = f"""🎥 Video Analysis Results:

**Analysis:** {text_response}

---
**Technical Details:**
- Model Used: {model_id}
- Region: {region}
- Video Path: {video_path}
- S3 URI: {s3_uri}
"""
        
        return {
            "status": "success",
            "content": [{"text": detailed_response}]
        }
        
    except ClientError as e:
        return {
            "status": "error",
            "content": [{"text": f"❌ AWS Error: {e.response['Error']['Message']}"}]
        }
    except Exception as e:
        return {
            "status": "error",
            "content": [{"text": f"❌ Error processing video: {str(e)}"}]
        }


def _get_video_format(file_path: str) -> Optional[str]:
    """Get video format from file extension."""
    formats = {
        '.mp4': 'mp4', '.mov': 'mov', '.avi': 'avi', 
        '.mkv': 'mkv', '.webm': 'webm'
    }
    
    if file_path.startswith('s3://'):
        filename = file_path.split('/')[-1]
    else:
        filename = os.path.basename(file_path)
    
    _, ext = os.path.splitext(filename.lower())
    return formats.get(ext)


def _upload_to_s3(local_path: str, bucket: str, session: boto3.Session) -> Optional[str]:
    """Upload video to S3 and return URI."""
    try:
        s3_client = session.client('s3')
        
        # Create bucket if needed
        try:
            s3_client.head_bucket(Bucket=bucket)
        except ClientError:
            try:
                if session.region_name == 'us-east-1':
                    s3_client.create_bucket(Bucket=bucket)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket,
                        CreateBucketConfiguration={'LocationConstraint': session.region_name}
                    )
            except ClientError:
                pass  # Bucket might already exist
        
        # Upload file
        filename = os.path.basename(local_path)
        s3_key = f"videos/{filename}"
        s3_client.upload_file(local_path, bucket, s3_key)
        
        return f"s3://{bucket}/{s3_key}"
        
    except Exception as e:
        print(f"Upload error: {e}")
        return None
