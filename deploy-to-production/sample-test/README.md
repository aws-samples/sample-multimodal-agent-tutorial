# AgentCore Memory Testing - Essential Scripts & Examples

Test scripts for validating memory functionality and multimodal capabilities of the deployed AgentCore travel assistant agent.

## Requirements

- Deployed AgentCore agent (see `../deployment/`)
- Agent ARN from deployment
- Python 3.10+ with boto3 installed
- AWS credentials configured

## Generate Test Content (Optional)

If you need sample travel images and videos for testing, use the travel content generator:

```bash
# Navigate to parent directory
cd ../..

# Open the content generator notebook
jupyter notebook 07-travel-content-generator.ipynb

# Generate images, videos, and itineraries for any destination
# Generated content will be saved to data-sample/ directory
```

This will create professional travel content that you can use with `test_image.py` and `test_video.py`.

## Interactive Testing - Jupyter Notebook

### AgentCore Memory Demo (`test_agentcore_memory.ipynb`)

**Interactive Jupyter notebook** demonstrating cross-session memory with the deployed AgentCore agent.

**What it demonstrates:**
- Short-term memory within a session
- Long-term memory across different sessions
- Multimodal content (images and videos)
- Memory persistence even after kernel restart
- User isolation with different user IDs

**Usage:**
```bash
# Install Jupyter if needed
pip install jupyter

# Launch notebook
jupyter notebook test_agentcore_memory.ipynb
```

**Configuration:**
1. Update `AGENT_ARN` with your deployed agent ARN
2. Update `AWS_REGION` if different from us-east-1
3. Run cells sequentially to see memory in action

**Key Features:**
- ✅ Persistent session and user IDs (memory survives notebook restart)
- ✅ Multiple sessions demonstrating cross-session memory
- ✅ Image and video analysis examples
- ✅ User isolation testing
- ✅ Pretty-printed conversation format

## Automated Test Scripts - 4 Testing Scenarios

### 1. Short-term Memory Test (`test_short_memory.py`)

Tests memory within a single session.

**What it tests:**
- Information storage within a session
- Memory recall in the same session
- Session-based context retention

**Usage:**
```bash
# Using environment variable
export AGENT_ARN="your-agent-arn"
python test_short_memory.py

# Or pass as argument
python test_short_memory.py YOUR_AGENT_ARN us-east-1
```

**Expected behavior:**
- First message stores travel preferences (name, food preferences, travel plans)
- Second message recalls the stored information from the same session

### 2. Long-term Memory Test (`test_long_memory.py`)

Tests memory persistence across different sessions.

**What it tests:**
- Information storage in one session
- Memory extraction and persistence
- Cross-session memory recall
- User-specific memory isolation

**Usage:**
```bash
# Using environment variable
export AGENT_ARN="your-agent-arn"
python test_long_memory.py

# Or pass as argument
python test_long_memory.py YOUR_AGENT_ARN us-east-1
```

**Expected behavior:**
- Session 1 stores detailed travel preferences (destination, dietary restrictions, budget)
- Session 2 (different session ID, same user) recalls the stored preferences
- Agent provides personalized recommendations based on stored memory

**Note:** Wait a few seconds between sessions for long-term memory extraction to complete.

### 3. Image Analysis Test (`test_image.py`)

Tests image analysis with memory integration.

**What it tests:**
- Image upload and analysis
- Image payload format (text + image)
- Memory of image content in follow-up questions
- Integration of visual and textual context

**Usage:**
```bash
# Set environment variable
export AGENT_ARN="your-agent-arn"

# Run test (region extracted automatically from ARN)
python test_image.py path/to/image.jpg
```

**Expected behavior:**
- First message analyzes the image (food, destination photo, etc.)
- Second message recalls image content and provides recommendations
- Agent combines visual analysis with stored user preferences

**Supported image formats:** JPEG, PNG, JPG, GIF, WebP

### 4. Video Analysis Test (`test_video.py`)

Tests video analysis with the travel agent.

**What it tests:**
- Video upload and analysis
- Video payload format (text + video)
- Memory of video content in follow-up questions
- Visual content analysis (no audio)

**Usage:**
```bash
# Set environment variable
export AGENT_ARN="your-agent-arn"

# Run test (region extracted automatically from ARN)
python test_video.py path/to/video.mp4
```

**Expected behavior:**
- First message analyzes the video (destinations, activities, cultural experiences)
- Second message creates an itinerary based on video content
- Agent combines visual analysis with stored user preferences

**Supported video formats:** MP4, MOV, AVI, MKV, WebM
**Maximum size:** ~20MB (for local processing)
**Note:** Video analysis is visual only (no audio processing)

## Session & User ID Management

### Session IDs
- Must be 33+ characters for proper AgentCore session management
- Different session IDs simulate different conversations
- Same session ID maintains conversation context

### User IDs
- Enable cross-session memory
- Same user ID across sessions allows memory persistence
- Different user IDs isolate memory between users

## Common Testing Issues & Solutions

**"No response from agent"**
- Verify agent ARN is correct
- Check agent is deployed: `cd ../deployment && agentcore status`
- Verify AWS credentials: `aws sts get-caller-identity`

**"Permission denied"**
- Ensure you have `bedrock-agentcore:InvokeAgentRuntime` permission
- Check IAM role/user has proper policies attached

**"Image file not found"**
- Verify image path is correct
- Use absolute path or relative path from current directory
- Check file exists: `ls -la path/to/image.jpg`

**Memory not persisting**
- Verify memory was enabled during `agentcore configure`
- Check `BEDROCK_AGENTCORE_MEMORY_ID` is set in deployment
- Wait a few seconds between sessions for memory extraction

**Region mismatch**
- Region is automatically extracted from the AGENT_ARN
- Ensure agent ARN is correct and properly formatted

## How to Find Your Agent ARN

After deploying with `agentcore launch`, get your ARN:

```bash
cd ../deployment
agentcore status
```

Or check the `.bedrock_agentcore.yaml` file:

```bash
cat ../deployment/.bedrock_agentcore.yaml | grep agent_arn
```

## Expected Test Output Examples

### Short-term Memory Test
```
Testing short-term memory in session: abc123...
Region: us-east-1
--------------------------------------------------
User: user-xyz...
Message 1: Setting travel preferences...
Session: abc123...
😊 Prompt 1: My name is Alice and I love Italian food...
🤖 Agent: Great to meet you, Alice! I'd love to help you plan your trip to Europe...

User: user-xyz...
Message 2: Testing memory recall...
Session: abc123...
😊 Prompt 2: What do you remember about my food preferences...
🤖 Agent: You mentioned your name is Alice and you love Italian food, especially pasta...

✓ Short-term memory test completed
```

## After Testing - Production Integration

After successful testing:
1. Monitor agent logs in CloudWatch
2. Review memory storage in Bedrock Console
3. Integrate agent with your application
4. Set up production monitoring and alerts

## Documentation Links

- [AgentCore Runtime Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html)
- [AgentCore Memory Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)
- [Programmatic Invocation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-toolkit.html#invoke-programmatically)
