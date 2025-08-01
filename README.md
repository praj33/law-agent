# Law Agent - Robust Legal AI Assistant

A comprehensive, scalable law agent system that serves both common people and law firms through intelligent agent-based interactions with reinforcement learning and dynamic interfaces.

## Features

- **Reinforcement Learning**: Self-improving agent that learns from user feedback
- **Agent Memory**: Persistent memory system for personalized interactions
- **Legal Domain Classification**: Intelligent categorization of legal queries
- **Dynamic Route Mapping**: Context-aware legal procedure guidance
- **Comprehensive Glossary**: Extensive legal terminology database
- **Adaptive UI**: Interface that adapts to user type and preferences
- **Scalable Architecture**: Built for high-performance and reliability

## Architecture

```
law_agent/
├── core/           # Core agent framework and configuration
├── agents/         # Specialized legal agents
├── rl/            # Reinforcement learning components
├── legal/         # Legal domain processing and knowledge
├── api/           # REST API endpoints
├── ui/            # User interface components
├── database/      # Database models and operations
├── utils/         # Utility functions and helpers
└── tests/         # Test suite
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black law_agent/
```

### Type Checking
```bash
mypy law_agent/
```

## Reinforcement Learning System

The RL system implements:
- **State**: User domain + feedback history
- **Action**: Legal domain → legal route → glossary
- **Reward**: User upvote/downvote + time spent metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
