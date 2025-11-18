# GuardianEye - Intelligent Security Operations Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

GuardianEye is a sophisticated, AI-powered Security Operations Center (SOC) platform built with Python and LangGraph. It streamlines security workflows and enhances threat detection and response by leveraging generative AI for intelligent analysis, automated reporting, and proactive threat hunting.

## 🎯 Overview

GuardianEye provides a comprehensive suite of AI-driven security agents that work together to monitor, analyze, and respond to security threats in real-time. The platform uses LangGraph for orchestrating complex agent workflows and maintaining state across multi-step security operations.

## ✨ Core Features

### Security Agent Modules

- **Incident Triage**: Automates security alert analysis, correlates events using threat intelligence, and suggests response actions
- **Vulnerability Prioritization**: Prioritizes remediation workflows by checking for exploits, mapping to asset inventory, and evaluating actual risk context
- **Anomaly Investigation**: Analyzes logs and user activity to detect suspicious behavior, comparing against established baselines
- **Threat Hunting**: Proactively searches for threats, maintains investigation states, and learns from previous threat hunts
- **Compliance Auditor**: Continuously checks configurations against compliance frameworks, maintains audit states, and generates reports
- **Recon Orchestrator**: Coordinates OSINT gathering, subdomain enumeration, and vulnerability identification to map the attack surface
- **Security Knowledge Graph**: Maintains a graph of the security architecture and past incidents, answering questions and providing context on the security posture

### Dashboard Interface

- Real-time visualization of security agent activities
- Overall system status monitoring
- Interactive security metrics and KPIs
- Historical trend analysis

### Configuration Management

- Flexible agent configuration using environment variables
- Support for multiple LLM providers
- Customizable model settings per agent

## 🏗️ Architecture

GuardianEye is built on a modern Python architecture leveraging:

- **LangGraph**: For orchestrating multi-agent workflows and maintaining state
- **LangChain**: For building AI-powered security agents
- **FastAPI**: For the backend API server
- **React/Next.js**: For the frontend dashboard (optional)
- **PostgreSQL/Redis**: For data persistence and caching

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip or poetry for package management
- PostgreSQL (optional, for persistent storage)
- Redis (optional, for caching)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ReDoubt
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or if using poetry
   poetry install
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   # LLM Configuration
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here

   # Database Configuration
   DATABASE_URL=postgresql://user:password@localhost:5432/guardianeye
   REDIS_URL=redis://localhost:6379/0

   # Agent Configuration
   DEFAULT_LLM_PROVIDER=openai
   DEFAULT_MODEL=gpt-4

   # API Configuration
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

5. **Initialize the database:**
   ```bash
   python -m guardianeye.db.init
   ```

6. **Run the application:**
   ```bash
   python -m guardianeye.main
   ```

The API server will be available at `http://localhost:8000`.

## 📁 Project Structure

```
ReDoubt/
├── guardianeye/              # Main application package
│   ├── agents/              # Security agent implementations
│   ├── graphs/              # LangGraph workflow definitions
│   ├── tools/               # Agent tools and utilities
│   ├── api/                 # FastAPI routes and endpoints
│   ├── db/                  # Database models and migrations
│   ├── config/              # Configuration management
│   └── utils/               # Shared utilities
├── tests/                   # Test suite
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment variables
└── README.md               # This file
```

## 🔧 Configuration

### Agent Configuration

Each security agent can be configured independently through the `.env` file or agent-specific configuration files:

```python
# Example agent configuration
INCIDENT_TRIAGE_MODEL=gpt-4
INCIDENT_TRIAGE_TEMPERATURE=0.3
INCIDENT_TRIAGE_MAX_TOKENS=2000

THREAT_HUNTING_MODEL=claude-3-opus
THREAT_HUNTING_TEMPERATURE=0.5
```

### LLM Provider Support

GuardianEye supports multiple LLM providers:
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Google (Gemini)
- Local models via Ollama

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=guardianeye

# Run specific test module
pytest tests/agents/test_incident_triage.py
```

## 📊 Monitoring and Logging

GuardianEye includes comprehensive logging and monitoring:

- Structured logging with JSON output
- Metrics collection for agent performance
- Distributed tracing support
- Error tracking and alerting

## 🛡️ Security Considerations

- All API keys and credentials should be stored in environment variables
- Use HTTPS in production environments
- Implement proper authentication and authorization
- Regular security audits of agent configurations
- Monitor and log all agent actions

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [LangChain](https://github.com/langchain-ai/langchain)
- UI components from [shadcn/ui](https://ui.shadcn.com/)

## 📞 Support

For questions, issues, or feature requests, please:
- Open an issue on GitHub
- Check our [documentation](docs/)
- Join our community discussions

---

**Note**: This project is under active development. Features and APIs may change.
