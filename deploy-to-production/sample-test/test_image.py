import json
import uuid
import boto3
import os
import sys
import base64

def test_image(agent_arn, image_path, region=None):
    """Test agent with image analysis"""
    
    # Extract region from ARN if not provided
    if not region:
        region = agent_arn.split(':')[3]
    
    # Initialize client
    client = boto3.client('bedrock-agentcore', region_name=region)
    
    # Generate session and user IDs
    session_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    print(f"Testing agent with image")
    print(f"Region: {region}")
    print(f"Image: {image_path}")
    print("-" * 50)
    
    try:
        # Read and encode image
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Determine image format from file extension
        image_format = image_path.split('.')[-1].lower()
        if image_format == 'jpg':
            image_format = 'jpeg'
        
        # Test 1: Send image with analysis request
        print(f"User: {user_id}")
        print(f"Session: {session_id}")
        print("Message 1: Analyzing travel-related image...")
        prompt = "I'm planning a trip and found this image. Can you analyze it and give me travel recommendations based on what you see? If it's food, tell me about the cuisine and where I can find similar dishes."
        print(f"😊 Prompt: {prompt}")
        
        # Prepare payload with image
        payload_data = {
            "prompt": prompt,
            "media": {
                "type": "image",
                "format": image_format,
                "data": image_data
            }
        }
        
        payload = json.dumps(payload_data).encode()
        
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
        
        print(f"🤖 Agent: {result}")
        print()
        
        # Test 2: Follow-up question (memory test)
        print(f"User: {user_id}")
        print(f"Session: {session_id}")
        print("Message 2: Testing memory of image analysis...")
        prompt2 = "Based on what you just saw in the image, can you create a travel itinerary for me? Include restaurants, activities, and cultural experiences related to what was in the photo."
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
        
        print(f"🤖 Agent: {result2}")
        
        print("\n✓ Image test completed")
        
    except FileNotFoundError:
        print(f"Error: Image file not found: {image_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    agent_arn = os.getenv('AGENT_ARN')
    
    if not agent_arn:
        print("❌ Error: AGENT_ARN environment variable not set")
        print("\nUsage:")
        print("  export AGENT_ARN='your-agent-arn'")
        print("  python test_image.py path/to/image.jpg")
        print("\nSupported formats: jpg, jpeg, png, gif, webp")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("❌ Error: Image path required")
        print("\nUsage: python test_image.py path/to/image.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found: {image_path}")
        sys.exit(1)
    
    region = agent_arn.split(':')[3]
    test_image(agent_arn, image_path, region)

if __name__ == "__main__":
    main()
