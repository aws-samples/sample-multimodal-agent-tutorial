"""
Video Reader Tool for Strands Agents - Local Version (No S3 Required)

This version processes videos locally by sending the video bytes directly to Bedrock,
eliminating the need for S3 bucket configuration and uploads.
"""
import boto3
import os
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
from strands import tool


@tool
def video_reader_local(
    video_path: str, 
    text_prompt: str = "Describe what you see in this video",
    model_id: str = "us.amazon.nova-pro-v1:0",
    region: Optional[str] = None,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze video content using AWS Bedrock's multimodal capabilities.
    
    This tool processes videos LOCALLY (no S3 upload required) and uses Nova/Claude 
    models to analyze video content through Bedrock's Converse API. The video is sent
    directly as bytes in the API request.
    
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
    
    TECHNICAL LIMITATIONS (Local Processing):
    - Maximum video size: ~20MB (Bedrock API limit for inline bytes)
    - For larger videos, use the S3-based version (video_reader.py)
    - Video must be in a supported format: mp4, mov, avi, mkv, webm
    
    Args:
        video_path: Path to local video file (must exist on filesystem)
        text_prompt: Question or instruction for analyzing the video
        model_id: Bedrock model ID to use for analysis (default: us.amazon.nova-pro-v1:0)
        region: AWS region for Bedrock client (default: from AWS_REGION env or us-west-2)
        system_prompt: Custom system prompt for analysis (optional)
        
    Returns:
        Dictionary with video analysis results containing:
        - status: "success" or "error"
        - content: List with text response from the model
        
    Example:
        >>> result = video_reader_local(
        ...     video_path="./my_video.mp4",
        ...     text_prompt="What activities are happening in this video?"
        ... )
        >>> print(result['content'][0]['text'])
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
            region = os.getenv('AWS_REGION', 'us-west-2')
        
        if not system_prompt:
            system_prompt = "Always answer in the same language you are asked. Note: I can only analyze visual content, not audio."
        
        # Validate file exists
        if not os.path.exists(video_path):
            return {
                "status": "error",
                "content": [{"text": f"❌ Video file not found: {video_path}"}]
            }
        
        # Determine video format
        video_format = _get_video_format(video_path)
        if not video_format:
            return {
                "status": "error",
                "content": [{"text": "❌ Unsupported video format. Supported: mp4, mov, avi, mkv, webm"}]
            }
        
        # Read video file and encode to base64
        with open(video_path, 'rb') as video_file:
            video_bytes = video_file.read()
        
        # Check file size (Bedrock has limits, typically ~20MB for videos)
        file_size_mb = len(video_bytes) / (1024 * 1024)
        if file_size_mb > 20:
            return {
                "status": "error",
                "content": [{"text": f"❌ Video file too large ({file_size_mb:.1f}MB). Maximum size is ~20MB. Consider compressing the video."}]
            }
        
        # Initialize Bedrock client
        session = boto3.Session(region_name=region)
        bedrock_client = session.client('bedrock-runtime')
        
        # Prepare message for Converse API with inline video data
        media_content = {
            'video': {
                "format": video_format,
                "source": {
                    'bytes': video_bytes
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
- File Size: {file_size_mb:.2f}MB
- Processing: Local (no S3 upload)
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
        '.mp4': 'mp4', 
        '.mov': 'mov', 
        '.avi': 'avi', 
        '.mkv': 'mkv', 
        '.webm': 'webm'
    }
    
    filename = os.path.basename(file_path)
    _, ext = os.path.splitext(filename.lower())
    return formats.get(ext)
