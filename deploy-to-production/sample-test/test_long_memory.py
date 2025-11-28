import json
import uuid
import boto3
import os
import sys
import time

def test_long_memory(agent_arn, region=None):
    """Test long-term memory across different sessions"""
    
    # Extract region from ARN if not provided
    if not region:
        region = agent_arn.split(':')[3]
    
    # Initialize client
    client = boto3.client('bedrock-agentcore', region_name=region)
    
    # Generate session IDs
    session_1 = str(uuid.uuid4())
    session_2 = str(uuid.uuid4())
    user_1 = str(uuid.uuid4())
    
    print(f"Testing long-term memory across sessions")
    print(f"Region: {region}")
    print("-" * 50)
    
    try:
        # Session 1: Store travel preferences
        print(f"User: {user_1}")
        print(f"Session 1: {session_1}")
        print("Storing travel preferences...")
        prompt1 = "My name is Sarah and I'm planning a trip to Japan. I'm vegetarian and I love visiting art museums and temples. My budget is around $3000."
        print(f"😊 Prompt 1: {prompt1}")
        
        payload1 = json.dumps({"prompt": prompt1}).encode()
        
        response1 = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_1,
            runtimeUserId = user_1,
            payload=payload1,
            qualifier="DEFAULT"
        )
        
        content1 = []
        for chunk in response1.get("response", []):
            content1.append(chunk.decode('utf-8'))
        
        result1 = json.loads(''.join(content1))
        print(f"🤖 Agent: {result1.get('result', 'No response')}")
        print()
        
        # Session 2: Test memory recall
        print(f"User: {user_1}")
        print(f"Session 2: {session_2}")
        print("Testing cross-session memory recall...")
        prompt2 = "What do you remember about my travel plans and preferences? Can you suggest some restaurants in Japan for me?"
        print(f"😊 Prompt 2: {prompt2}")
        
        payload2 = json.dumps({"prompt": prompt2}).encode()        
        response2 = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_2,  # Different session
            runtimeUserId = user_1,
            payload=payload2,
            qualifier="DEFAULT"
        )
        
        content2 = []
        for chunk in response2.get("response", []):
            content2.append(chunk.decode('utf-8'))
        
        result2 = json.loads(''.join(content2))
        print(f"🤖 Agent: {result2.get('result', 'No response')}")
        
        print("\n✓ Long-term memory test completed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    agent_arn = os.getenv('AGENT_ARN')
    region = os.getenv('AWS_REGION')
    
    if len(sys.argv) > 1:
        agent_arn = sys.argv[1]
    if len(sys.argv) > 2:
        region = sys.argv[2]
    
    if not agent_arn:
        print("Usage: python test_long_memory.py <AGENT_ARN> [REGION]")
        print("Or set AGENT_ARN environment variable")
        sys.exit(1)
    
    test_long_memory(agent_arn, region)

if __name__ == "__main__":
    main()
