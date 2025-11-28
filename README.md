# Strands Agents Tutorial - Build Multi-Modal AI

## Overview

Build production-ready AI agents with the [Strands Agents SDK](https://github.com/strands-agents/sdk-python) and AWS services. This repository demonstrates how you can create multi-modal systems with persistent memory in minimal code. Progress from your first agent to production-ready systems through hands-on chapters.

Strands Agents create AI agents with minimal code using built-in tools from the community package. No need to write custom tool implementations—focus on your use case while the framework handles the complexity.

## Tutorial Contents - 7 Hands-On Notebooks + Production Deploy

| # | Notebook | Description |
|---|----------|-------------|
| **01** | [Hello World - First AI Agent](notebooks/01-hello-world-strands-agents.ipynb) | Create your first AI agent with [Amazon Bedrock](https://aws.amazon.com/bedrock/) in under 10 lines of code. Learn agent basics, system prompts, and execution loops. |
| **02** | [Custom Tools for Multi-Modal Processing](notebooks/02-custom-tools.ipynb) | Extend agents with custom tools using the `@tool` decorator. Process multi-modal content including images, videos, and documents. |
| **03** | [MCP Integration for Tool Sharing](notebooks/03-mcp-integration.ipynb) | Share tools across applications with [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). Convert tools to MCP servers and deploy for production. |
| **04** | [State Management and Sessions](notebooks/04-state-and-sessions.ipynb) | Implement session management with `FileSessionManager`. Maintain conversation context and handle multiple concurrent sessions. |
| **05** ⭐ | [S3 Vector Memory for Persistent Context](notebooks/05-s3-vector-memory.ipynb) | Build semantic memory with [Amazon S3 Vectors](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html). Create agents that remember across all sessions with production-ready infrastructure. |
| **06** 🌍 | [Travel Assistant with Cross-Session Memory](notebooks/06-travel-assistant-demo.ipynb) | Real-world demonstration of cross-session memory with a personalized AI travel assistant. Features multimodal analysis (text, images, PDFs) and progressive personalization. |
| **07** 🎨 | [Travel Content Generator with Built-in Tools](notebooks/07-travel-content-generator.ipynb) | Generate complete travel content packages (images, videos, itineraries) for any destination using built-in tools from [`strands-agents-tools`](https://pypi.org/project/strands-agents-tools/). Fully automated with no manual confirmations. |
| **Bonus** 🚀 | [Deploy to Production with AgentCore](deploy-to-production/) | Deploy your multimodal travel agent to production using [Amazon Bedrock AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html). Includes persistent memory, serverless deployment, and comprehensive testing. |

### Recommended Learning Path

- **Notebooks 01-02**: Basic agents with custom capabilities
- **Notebook 03**: Production-ready tools with MCP standardization
- **Notebooks 04-05**: Stateful agents with persistent memory
- **Notebooks 06-07**: Real-world applications demonstrating rapid development with built-in tools

## Quick Start

### Prerequisites
- AWS Account with [Amazon Bedrock](https://aws.amazon.com/bedrock/) model access enabled
- Python 3.9+ and Jupyter Notebook
- AWS CLI configured (`aws configure`)

### Installation

```bash
# Setup environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
cd notebooks
pip install -r requirements.txt

```

Open `notebooks/01-hello-world-strands-agents.ipynb` to begin.

## Why Strands Agents - Key Advantages

### Build Faster with 40+ Pre-Built Tools

Building AI agents traditionally requires extensive boilerplate code for tool integration, error handling, and state management. Strands Agents provides:

**Built-in Tools**: The [`strands-agents-tools`](https://pypi.org/project/strands-agents-tools/) package includes 40+ pre-built tools:
- **Multi-modal**: `generate_image`, `image_reader`, `nova_reels`, `diagram`
- **File Operations**: `file_read`, `file_write`, `editor`
- **Memory**: `memory`, `agent_core_memory`, `mem0_memory`
- **Web & Network**: `http_request`, `browser`, `slack`
- **AWS Services**: `use_aws`, `retrieve` (Bedrock Knowledge Bases)
- **Code Execution**: `python_repl`, `code_interpreter`
- **And many more**: See [full list](https://github.com/strands-agents/tools)

**Example**: Create an agent with image generation in 5 lines:

```python
from strands import Agent
from strands.models import BedrockModel
from strands_tools import generate_image

agent = Agent(model=BedrockModel(model_id="..."), tools=[generate_image])
agent("Generate an image of the Eiffel Tower at sunset")
```

No need to write image generation logic, handle API calls, or manage file storage—the tool handles everything.

### 4-Step Rapid Prototyping Process

Test new ideas quickly:

1. **Import pre-built tools** from strands-agents-tools
2. **Create an agent** with your chosen model
3. **Add tools** to the agent's capabilities
4. **Run and iterate** immediately

This repository demonstrates this approach throughout—especially in the Travel Content Generator (Notebook 08) where you can generate complete content packages with minimal custom code.

## Real-World Demo - AI Travel Assistant with Memory

Experience persistent vector memory with a real-world use case: an AI travel assistant that remembers your preferences across multiple sessions.

### Key Features

- **True Cross-Session Memory**: Agent remembers everything even with fresh instances
- **Multimodal Analysis**: Processes text preferences, destination photos, and travel itineraries
- **Semantic Search**: Finds relevant memories intelligently
- **Progressive Personalization**: Gets smarter with each interaction
- **Production-Ready**: Built on AWS services for scale

### Try the Demo

```bash
# 1. Open the demo notebook
notebook notebooks/06-travel-assistant-demo.ipynb

# 2. Update configuration with your S3 Vector bucket
# 3. Run all cells to see cross-session memory in action
```

**Note**: To generate custom travel content for the demo, open and run [notebooks/07-travel-content-generator.ipynb](notebooks/07-travel-content-generator.ipynb) first.

## Production Deployment - AgentCore Runtime Guide

Take your multimodal travel agent from notebook to production with [Amazon Bedrock AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html).

### What's Included

The [`deploy-to-production/`](deploy-to-production/) directory contains everything you need to deploy a production-ready multimodal travel agent:

- **Persistent Memory**: Cross-session memory using Bedrock AgentCore Memory
- **Multimodal Support**: Process images, videos, and documents
- **Serverless Deployment**: Auto-scaling with AWS CodeBuild (no Docker required)
- **Test Scripts**: Comprehensive testing for memory and multimodal capabilities

### Features

- ✅ **Image Analysis**: Analyze destination photos, food labels, travel documents
- ✅ **Video Processing**: Process travel videos with Amazon Nova (visual only)
- ✅ **Document Reading**: Read PDFs, itineraries, and text files
- ✅ **Memory Persistence**: Remember user preferences across all sessions
- ✅ **Production Monitoring**: CloudWatch logs and metrics

### Quick Deploy

```bash
# 1. Navigate to deployment directory
cd deploy-to-production/deployment

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure agent with memory
agentcore configure -e multimodal_agent.py
# Select 'yes' for memory and long-term memory extraction

# 4. Deploy to production
agentcore launch

```

### Testing - Memory & Multimodal Capabilities

```bash
# Test short-term and long-term memory
cd ../sample-test
export AGENT_ARN="your-agent-arn"
python test_short_memory.py
python test_long_memory.py

# Test image and video analysis
python test_multimodal.py path/to/image.jpg
python test_video.py path/to/video.mp4
```

**Learn More**: See the complete [deployment guide](deploy-to-production/README.md) for detailed instructions, architecture diagrams, and troubleshooting.


## Best Practices & Tips

- Complete notebooks in order—each builds on previous concepts
- Run cells sequentially to maintain state
- Experiment with examples to deepen understanding
- Explore the [strands-agents-tools package](https://github.com/strands-agents/tools) for more pre-built capabilities
- Monitor costs with [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/)

## Common Issues & Solutions

**Import Errors**: Run `pip install --upgrade strands-agents strands-agents-tools boto3`

**AWS Credentials**: Verify with `aws sts get-caller-identity` or reconfigure with `aws configure`

**S3 Vectors** (Notebook 05): Follow the [Getting Started Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-getting-started.html) and verify bucket and index regions match

**MCP Server** (Notebook 03): Ensure server runs on `http://localhost:8000/sse` with no port conflicts

**Tool Consent Prompts**: Set `BYPASS_TOOL_CONSENT=true` environment variable for automated workflows

## Additional Resources

**Documentation**  
• [Strands Agents SDK](https://github.com/strands-agents/sdk-python)  
• [Strands Community Tools](https://github.com/strands-agents/tools)  
• [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/)  
• [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)  
• [S3 Vectors](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html)  
• [MCP Specification](https://modelcontextprotocol.io/)  
• [Amazon Nova](https://aws.amazon.com/bedrock/nova/)

---

**Ready to start?** Open [Notebook 01: Hello World](notebooks/01-hello-world-strands-agents.ipynb) and build your first AI agent.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

