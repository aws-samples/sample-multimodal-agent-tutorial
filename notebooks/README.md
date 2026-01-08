# Strands Agents - Tutorial Notebooks

## Overview

This directory contains 8 hands-on Jupyter notebooks that guide you through building production-ready AI agents with the Strands Agents SDK and AWS services. The notebooks build on previous concepts, taking you from basic agent creation to deploying multimodal systems with persistent memory.

## Notebooks

| # | Notebook | Description |
|---|----------|-------------|
| **01** | [Hello World - First AI Agent](01-hello-world-strands-agents.ipynb) | Create your first AI agent with [Amazon Bedrock](https://aws.amazon.com/es/bedrock/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) in under 10 lines of code. Learn agent basics, system prompts, and execution loops. |
| **02** | [Custom Tools for Multi-Modal Processing](02-custom-tools.ipynb) | Extend agents with custom tools using the `@tool` decorator. Process multi-modal content including images, videos, and documents. |
| **03** | [MCP Integration for Tool Sharing](03-mcp-integration.ipynb) | Share tools across applications with [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). Convert tools to MCP servers and deploy for production. |
| **04** | [State Management and Sessions](04-state-and-sessions.ipynb) | Implement session management with `FileSessionManager`. Maintain conversation context and handle multiple concurrent sessions. |
| **05** ⭐ | [S3 Vector Memory for Persistent Context](05-s3-vector-memory.ipynb) | Build semantic memory with [Amazon S3 Vectors](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html). Create agents that remember across all sessions with production-ready infrastructure. |
| **06** 🌍 | [Travel Assistant with Cross-Session Memory](06-travel-assistant-demo.ipynb) | Real-world demonstration of cross-session memory with a personalized AI travel assistant. Features multimodal analysis (text, images, PDFs) and progressive personalization. |
| **07** 🎨 | [Travel Content Generator with Built-in Tools](07-travel-content-generator.ipynb) | Generate complete travel content packages (images, videos, itineraries) for any destination using built-in tools from [`strands-agents-tools`](https://pypi.org/project/strands-agents-tools/). Fully automated with no manual confirmations. |
| **08** 🎬 | [Agentic Video Analysis](08-agentic-video-analysis.ipynb) | Build specialized video analysis agents using TwelveLabs API or AWS Bedrock Pegasus. Upload videos, generate insights, and query video content with natural language. |

## Quick Start

### Prerequisites
- AWS Account with [Amazon Bedrock](https://aws.amazon.com/es/bedrock/?trk=87c4c426-cddf-4799-a299-273337552ad8&sc_channel=el) model access enabled
- Python 3.9+ and Jupyter Notebook
- AWS CLI configured (`aws configure`)

### Installation

```bash
# Navigate to notebooks directory
cd notebooks

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

```

## Recommended Learning Path

1. **Notebooks 01-02**: Basic agents with custom capabilities
2. **Notebook 03**: Production-ready tools with MCP standardization
3. **Notebooks 04-05**: Stateful agents with persistent memory
4. **Notebooks 06-07**: Real-world applications demonstrating rapid development with built-in tools

## Support Files

- **data-sample/**: Sample images, PDFs, and videos for hands-on exercises
- **s3_memory.py**: Custom S3 Vector memory implementation for persistent context
- **travel_content_generator.py**: Tools for generating travel content packages
- **video_reader.py** / **video_reader_local.py**: Video processing utilities for multimodal agents
- **twelvelabs_video_tool.py**: TwelveLabs API integration for advanced video understanding
- **bedrock_video_tool.py**: AWS Bedrock Pegasus integration for direct video analysis

## Tips

- Complete notebooks in sequential order for best learning experience
- Run all cells in order to maintain proper state
- Experiment with the examples to deepen your understanding
- Check the main [README](../README.md) for troubleshooting and additional resources

## Next Steps

After completing the notebooks, explore:
- [Deploy to Production](../deploy-to-production/) - Deploy your agent with Amazon Bedrock AgentCore Runtime
- [Strands Community Tools](https://github.com/strands-agents/tools) - 40+ pre-built tools for rapid development
- [Strands Agents SDK Documentation](https://github.com/strands-agents/sdk-python) - Complete SDK reference

---

**Ready to start?** Open [01-hello-world-strands-agents.ipynb](01-hello-world-strands-agents.ipynb) and build your first AI agent!
