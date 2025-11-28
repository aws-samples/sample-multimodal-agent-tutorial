import json
import uuid
import boto3
import os
import sys
import base64

def test_video(agent_arn, video_path, region=None):
    """Test video analysis with the travel agent"""
    
    # Extract region from ARN if not provided
    if not region:
        region = agent_arn.split(':')[3]
    
    # Initialize client
    client = boto3.client('bedrock-agentcore', region_name=region)
    
    # Generate session and user IDs
    session_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    print(f"Testing video analysis with travel agent")
    print(f"Region: {region}")
    print(f"Video: {video_path}")
    print("-" * 50)
    
    try:
        # Check file size
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        if file_size_mb > 20:
            print(f"⚠️  Warning: Video is {file_size_mb:.1f}MB. Maximum recommended size is 20MB.")
            print("Consider compressing the video for better performance.")
            return
        
        print(f"📹 Video size: {file_size_mb:.2f}MB")
        
        # Read and encode video
        with open(video_path, 'rb') as video_file:
            video_data = base64.b64encode(video_file.read()).decode('utf-8')
        
        # Determine video format from file extension
        video_format = video_path.split('.')[-1].lower()
        
        # Test 1: Send video with analysis request
        print(f"\nUser: {user_id}")
        print(f"Session: {session_id}")
        print("Message 1: Analyzing travel video...")
        prompt = "Please analyze this travel video and tell me about the destination, activities, and cultural experiences shown. Provide recommendations for similar destinations."
        print(f"😊 Prompt: {prompt}")
        
        # Prepare payload with video
        payload_data = {
            "prompt": prompt,
            "media": {
                "type": "video",
                "format": video_format,
                "data": video_data
            }
        }
        
        payload = json.dumps(payload_data).encode()
        
        print("⏳ Sending video to agent (this may take a moment)...")
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            runtimeUserId=user_id,
            payload=payload,
            qualifier="DEFAULT"
        )
        
        # Parse response
        content = []
        for chunk in response.get("response", []):
            content.append(chunk.decode('utf-8'))
        
        if content:
            response_text = ''.join(content)
            try:
                response_json = json.loads(response_text)
                result = response_json.get("result", response_text)
            except json.JSONDecodeError:
                result = response_text
        else:
            result = "No response from agent"
        
        print(f"\n🤖 Agent: {result}")
        print()
        
        # Test 2: Follow-up question (memory test)
        print(f"User: {user_id}")
        print(f"Session: {session_id}")
        print("Message 2: Testing memory of video analysis...")
        prompt2 = "Based on what you saw in the video, can you create a 3-day itinerary for me with similar activities and experiences?"
        print(f"😊 Prompt: {prompt2}")
        
        payload2 = json.dumps({"prompt": prompt2}).encode()
        
        response2 = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,  # Same session
            runtimeUserId=user_id,
            payload=payload2,
            qualifier="DEFAULT"
        )
        
        content2 = []
        for chunk in response2.get("response", []):
            content2.append(chunk.decode('utf-8'))
        
        if content2:
            response_text2 = ''.join(content2)
            try:
                response_json2 = json.loads(response_text2)
                result2 = response_json2.get("result", response_text2)
            except json.JSONDecodeError:
                result2 = response_text2
        else:
            result2 = "No response from agent"
        
        print(f"\n🤖 Agent: {result2}")
        
        print("\n✓ Video analysis test completed")
        print("\n📝 Note: Video analysis is visual only (no audio processing)")
        
    except FileNotFoundError:
        print(f"❌ Error: Video file not found: {video_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    agent_arn = os.getenv('AGENT_ARN')
    
    if not agent_arn:
        print("❌ Error: AGENT_ARN environment variable not set")
        print("\nUsage:")
        print("  export AGENT_ARN='your-agent-arn'")
        print("  python test_video.py path/to/video.mp4")
        print("\nSupported formats: mp4, mov, avi, mkv, webm")
        print("Maximum size: ~20MB")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("❌ Error: Video path required")
        print("\nUsage: python test_video.py path/to/video.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"❌ Error: Video file not found: {video_path}")
        sys.exit(1)
    
    region = agent_arn.split(':')[3]
    test_video(agent_arn, video_path, region)

if __name__ == "__main__":
    main()
