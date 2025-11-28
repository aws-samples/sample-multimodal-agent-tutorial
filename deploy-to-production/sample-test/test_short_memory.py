import json
import uuid
import boto3
import os
import sys

def test_short_memory(agent_arn, region=None):
    """Test short-term memory within a single session"""
    
    # Extract region from ARN if not provided
    if not region:
        region = agent_arn.split(':')[3]
    
    # Initialize client
    client = boto3.client('bedrock-agentcore', region_name=region)
    
    # Generate session ID
    session_id = str(uuid.uuid4())

    # Generate user ID
    user_id = str(uuid.uuid4())
    
    print(f"Testing short-term memory in session: {session_id}")
    print(f"Region: {region}")
    print("-" * 50)
    
    try:
        # First message - establish travel context
        print(f"User: {user_id}")
        print("Message 1: Setting travel preferences...")
        print(f"Session: {session_id}")
        prompt = "My name is Alice and I love Italian food, especially pasta. I'm planning a trip to Europe."
        print("😊 Prompt 1: ",prompt)
        payload1 = json.dumps({"prompt": prompt}).encode()
        
        response1 = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            runtimeUserId = user_id,
            payload=payload1,
            qualifier="DEFAULT"
        )
        
        content1 = []
        for chunk in response1.get("response", []):
            content1.append(chunk.decode('utf-8'))
        
        result1 = json.loads(''.join(content1))
        print(f"🤖 Agent: {result1.get('result', 'No response')}")
        print()
        
        # Second message - test memory recall
        print(f"User: {user_id}")
        print("Message 2: Testing memory recall...")
        print(f"Session: {session_id}")
        prompt = "What do you remember about my food preferences and travel plans?"
        print("😊 Prompt 2: ",prompt)
        payload2 = json.dumps({"prompt": prompt}).encode()

        response2 = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,  # Same session
            runtimeUserId = user_id,
            payload=payload2,
            qualifier="DEFAULT"
        )
        
        content2 = []
        for chunk in response2.get("response", []):
            content2.append(chunk.decode('utf-8'))
        
        result2 = json.loads(''.join(content2))
        print(f"🤖 Agent: {result2.get('result', 'No response')}")
        
        print("\n✓ Short-term memory test completed")
        
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
        print("Usage: python test_short_memory.py <AGENT_ARN> [REGION]")
        print("Or set AGENT_ARN environment variable")
        sys.exit(1)
    
    test_short_memory(agent_arn, region)

if __name__ == "__main__":
    main()
