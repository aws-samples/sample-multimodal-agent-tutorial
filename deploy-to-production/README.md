# Deploy AI Agents to Production - Complete AgentCore Guide

## Overview

Deploy the multimodal travel assistant agent to production using [Amazon Bedrock AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html). This agent features persistent memory, multimodal content analysis (images, videos, documents), and personalized travel recommendations.

### AgentCore Services

- **[AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html)** ⭐ - Serverless execution with auto-scaling and session management
- **[AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html)** - Secure credential management for API keys and tokens  
- **[AgentCore Memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)** ⭐ - State persistence and conversation history
- **[AgentCore Code Interpreter](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-tool.html)** - Secure code execution sandbox
- **[AgentCore Browser](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-tool.html)** - Cloud browser automation
- **[AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)** - API management and tool discovery
- **[AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html)** - Monitoring, tracing, and debugging
- **[AgentCore Policy](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html)** - Deterministic control and security boundaries for agent-tool interactions
- **[AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html)** - Automated assessment and performance measurement for agents

## Production Features

- **Persistent Memory**: Cross-session memory using Bedrock AgentCore Memory
  - **Short-term Memory**: Captures turn-by-turn interactions within a single session
  - **Long-term Memory**: Automatically extracts and stores key insights across multiple sessions
- **Multimodal Analysis**: Process images, videos, and documents with built-in tools
- **Travel Expertise**: Personalized recommendations based on user preferences
- **Production Ready**: Secure, scalable deployment on AWS infrastructure

## Requirements & Setup

- **AWS Account** with [appropriate permissions](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-permissions.html)
- **Python 3.10+** installed
- **AWS CLI configured** (`aws configure`)
- **Model Access**: Enable `us.anthropic.claude-3-5-sonnet-20241022-v2:0` in Amazon Bedrock console
- Basic understanding of [AI agents](https://aws.amazon.com/what-is/ai-agents/) and [AWS services](https://aws.amazon.com/what-is-aws/)

## Installation

```bash
# Navigate to deployment directory
cd deploy-to-production/deployment

# Create virtual environment (optional, can use parent directory)
python3 -m venv ../.venv
source ../.venv/bin/activate  # Windows: ..\.venv\Scripts\activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Verify installation
agentcore --help
```

## 3-Step Deployment Process

### Step 1: Configure

Navigate to deployment directory and configure the agent with memory enabled:

```bash
cd deployment
agentcore configure -e multimodal_agent.py
# Select 'yes' for memory
# Select 'yes' for long-term memory extraction
```

Or specify a different region:

```bash
agentcore configure -e multimodal_agent.py -r us-east-1
```

### Custom Header Configuration

Select YES in *Request Header Allow list*, and in *Request Header Allow* paste `X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actor-Id`

This header allows passing a user identifier from your application to the agent. The agent extracts it from `context.request_headers` (normalized to lowercase: `x-amzn-bedrock-agentcore-runtime-custom-actor-id`) and uses it to namespace memory per user.

At the end `.bedrock_agentcore.yaml`, must look like this: 

```yaml
request_header_configuration:
  requestHeaderAllowlist:
  - X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actor-Id
```

This creates a `.bedrock_agentcore.yaml` configuration file.

**Note**: When you enable memory during configuration, the AgentCore CLI automatically creates the memory resource (if needed) and sets the `BEDROCK_AGENTCORE_MEMORY_ID` environment variable during deployment. Your agent code reads this variable automatically.

### Step 2: Deploy

Deploy to Amazon Bedrock AgentCore Runtime:

```bash
agentcore launch
```

This command:
- Builds your container using AWS CodeBuild (no Docker required)
- Creates necessary AWS resources (ECR repository, IAM roles)
- Deploys your agent to AgentCore Runtime
- Configures CloudWatch logging
- Sets up memory if enabled

**Note the Agent ARN** from the output - you'll need it to invoke the agent.

### Step 3: Test Memory Functionality

For automated testing, use the provided test applications in `sample-test/`:

```bash
# Set your agent ARN (get from agentcore status or agentcore launch output)
export AGENT_ARN="your-agent-arn-from-step-2"
```

**Test short-term memory (within session):**

Captures turn-by-turn interactions within a single session. Agents maintain immediate context without requiring users to repeat information.

```bash
cd sample-test
python test_short_memory.py
```

This script tests:
- Information storage within a session
- Memory recall in the same session
- Session-based context retention


**Test long-term memory (across sessions):**

Automatically extracts and stores key insights from conversations across multiple sessions, including user preferences, important facts, and session summaries.

```bash
cd sample-test
python test_long_memory.py
```

This script tests:
- Information storage in one session
- Memory extraction and persistence
- Cross-session memory recall
- User-specific memory isolation

**Important:** Long-term memory extraction is an [asynchronous background process](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/long-term-saving-and-retrieving-insights.html#long-term-step-2-retrieve-extracted-insights) that can take a minute or more. The test waits 60 seconds between invocations for reliable memory retrieval.

**Generate test content (optional):**

If you need sample travel content for testing, use the travel content generator from the parent directory:

```bash
cd ..
07-travel-content-generator.ipynb
# Generate images, videos, and itineraries for any destination
# Generated content will be saved to data-sample/ directory
cd deploy-to-production/sample-test
```

**Test multimodal capabilities:**

```bash
python test_image.py path/to/image.jpg
```

```bash
# Run the video test with a sample video
python test_video.py path/to/video.mp4
```

This script tests:
- Video analysis with the agent (visual only, no audio)
- Memory of video content in follow-up questions
- Multimodal payload format (text + video)
- Maximum video size: ~20MB

**Interactive Notebook**

For an interactive experience, use the Jupyter notebook:

```bash
cd sample-test
#go to notebook test_agentcore_memory.ipynb
```

The notebook demonstrates:
- ✅ Cross-session memory persistence
- ✅ Multimodal content (images and videos)
- ✅ Memory survival across kernel restarts
- ✅ User isolation testing
- ✅ Pretty-printed conversations

**If you want to start using the agent by creating your own code, keep the following points in mind**:
- Session IDs must be 33+ characters for proper session management
- Use custom headers for user identification: `X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actor-Id`
- Same user ID enables cross-session memory
- Different session IDs simulate different conversations
- Headers are normalized to lowercase in the agent code


## Locate AWS Resources After Deployment

After deployment, find resources in AWS Console:

| Resource | Location |
|----------|----------|
| **Agent Logs** | CloudWatch → Log groups → `/aws/bedrock-agentcore/runtimes/{agent-id}-DEFAULT` |
| **Container Images** | ECR → Repositories → `bedrock-agentcore-multimodal_agent` |
| **Build Logs** | CodeBuild → Build history |
| **IAM Role** | IAM → Roles → Search for "BedrockAgentCore" |
| **Memory Store** | Bedrock Console → AgentCore → Memory |

You can also check your agent status:

```bash
cd deployment
agentcore status
```

## 3 Deployment Options - Cloud, Local & Hybrid

### Default: CodeBuild (Recommended)

No Docker required - builds in the cloud:

```bash
agentcore launch
```

### Local Development

Build and run locally (requires Docker):

```bash
agentcore launch --local
```

### Hybrid: Local Build + Cloud Runtime

Build locally, deploy to cloud (requires Docker):

```bash
agentcore launch --local-build
```

## Agent Code Architecture & Memory Integration

The agent uses [AgentCore Memory SDK](https://github.com/aws/bedrock-agentcore-sdk-python/tree/main/src/bedrock_agentcore/memory) for integration with Strands Agents.

### Automatic Memory Setup

When you run `agentcore configure` and enable memory, the AgentCore CLI automatically creates the memory resource (if needed) and sets the `BEDROCK_AGENTCORE_MEMORY_ID` environment variable during `agentcore launch`. Your agent code reads this variable automatically - no manual configuration needed.

Memory automatically stores:
- Travel preferences and interests
- Dietary restrictions
- Budget considerations
- Past travel experiences
- User facts and context

### Basic Memory Setup
```python
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig

# Create memory client
client = MemoryClient(region_name="us-west-2") #your region

# Create memory store
basic_memory = client.create_memory(
    name="BasicTestMemory",
    description="Basic memory for testing short-term functionality"
)

# Configure memory with retrieval settings
memory_config = AgentCoreMemoryConfig(
    memory_id=basic_memory.get('id'),
    session_id=session_id,
    actor_id=actor_id,
    retrieval_config={
        f"/users/{actor_id}/facts": RetrievalConfig(top_k=3, relevance_score=0.5),
        f"/users/{actor_id}/preferences": RetrievalConfig(top_k=3, relevance_score=0.5)
    }
)
```

### Memory Integration with Strands Agents

```python
_agent = Agent(
            model=BedrockModel(model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0"),
            tools=[image_reader, file_read,video_reader_local],
            system_prompt=system_prompt,
            session_manager=session_manager
```

The `invoke` function is the main entry point for your AgentCore agent:

- Receives user prompts and context from AgentCore Runtime
- Extracts session and actor IDs for memory management
- Creates or retrieves the agent instance with memory configuration
- Processes the user message and returns the response

```python
@app.entrypoint
def invoke(payload, context):
    """AgentCore Runtime entry point with lazy-loaded agent"""
    # Extract user prompt
    prompt = payload.get("prompt", "Hello!")
    
    # Get session/actor info for memory
    actor_id = context.request_headers.get('X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actor-Id', 'whatsapp-user')
    session_id = context.session_id or 'whatsapp-session'
    
    # Get agent with memory
    agent = get_or_create_agent(actor_id, session_id)
    
    # Handle multimodal input (images)
    if "media" in payload:
        media = payload["media"]
        if media.get("type") == "image":
            # Process image with agent tools
            image_data = base64.b64decode(media["data"])
            # ... image processing logic
    
    # Process and return response
    result = agent(prompt)
    return {"result": result.message}
```

### Sending Images, Videos & Text - Payload Examples

#### Sending Images

To send images to the agent, use this payload structure:

```python
import base64

# Read and encode image
with open("destination.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Create payload
payload = {
    "prompt": "What can you tell me about this destination?",
    "media": {
        "type": "image",
        "format": "jpeg",  # or "png", "jpg", "gif", "webp"
        "data": image_data  # base64-encoded string
    }
}
```

**How it works:**
1. Client sends image as base64 in payload
2. Agent decodes and saves temporarily to `/tmp/`
3. Agent instructs itself to use `image_reader` tool with the temp file path
4. Tool reads the file and sends bytes directly to Claude model
5. Model analyzes the image and responds

#### Sending Videos

Videos follow the same pattern but are processed by the `video_reader_local` tool:

```python
import base64

# Read and encode video
with open("travel_vlog.mp4", "rb") as f:
    video_data = base64.b64encode(f.read()).decode('utf-8')

# Create payload
payload = {
    "prompt": "Analyze this travel video and suggest similar destinations",
    "media": {
        "type": "video",
        "format": "mp4",  # or "mov", "avi", "mkv", "webm"
        "data": video_data  # base64-encoded string
    }
}
```

**Video limitations:**
- Maximum size: ~20MB (for local processing)
- Visual content only (no audio analysis)
- Supported formats: mp4, mov, avi, mkv, webm

#### Text-Only Messages

For text-only messages, simply send the prompt:

```python
payload = {
    "prompt": "I want to visit Japan. What should I know?"
}
```



## Common Deployment Issues & Fixes

**Permission denied errors**
- Verify AWS credentials: `aws sts get-caller-identity`
- Check required policies are attached

**Docker not found warnings**
- Ignore if using default CodeBuild deployment
- Only needed for `--local` or `--local-build` modes

**Model access denied**
- Enable Claude 3.5 Sonnet in Bedrock console
- Verify correct AWS Region

**Port 8080 in use (local only)**
- Find process: `lsof -ti:8080`
- Stop process: `kill -9 PID`

For more troubleshooting, see [AgentCore Runtime Troubleshooting](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-troubleshooting.html).

## Delete Resources & Clean Up

Delete all AWS resources created by the toolkit:

```bash
cd deployment
agentcore destroy
```

**Note**: This will delete the agent runtime but not the memory store. To delete the memory store, go to the Bedrock Console → AgentCore → Memory.

## Additional Documentation & Resources

**Documentation**
- [What is Amazon Bedrock AgentCore?](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- [AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html)
- [AgentCore Memory Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)
- [AgentCore Memory SDK](https://github.com/aws/bedrock-agentcore-sdk-python/tree/main/src/bedrock_agentcore/memory)
- [Starter Toolkit Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-toolkit.html)
- [Strands Agents SDK](https://strandsagents.com/latest/documentation/docs/)

**Code Examples**
- [AWS Labs AgentCore Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)

**Related Notebooks**
- [06-travel-assistant-demo.ipynb](../06-travel-assistant-demo.ipynb) - Interactive demo with cross-session memory
- [07-travel-content-generator.ipynb](../07-travel-content-generator.ipynb) - Generate test content for multimodal testing
- [05-s3-vector-memory.ipynb](../05-s3-vector-memory.ipynb) - Memory implementation with S3 Vectors
- [02-custom-tools.ipynb](../02-custom-tools.ipynb) - Custom tool development


**Ready to deploy?** Follow the Quick Start guide above to get your multimodal travel agent running in minutes.
