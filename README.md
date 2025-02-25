# Living Game Templates

A collection of PyGame-based game templates and concepts to kickstart your game development journey.

## Overview

This repository contains various game templates implemented in PyGame, along with concept documents in Excalidraw SVG format. Each template serves as a starting point for different game genres.

## Swarm Agents System

The project includes a sophisticated multi-agent system that enables complex emergent behaviors and interactions:

### Agent Types
- **Designer Agent**: Focuses on creating innovative and original gameplay mechanics
- **Developer Agent**: Specializes in implementing novel game mechanics in Python
- **Concept Agent**: Generates and manages game concepts and descriptions

### Using the Agents
```bash
# Run a conversation between agents
python swarm/run_conversation.py --prompt "Your game concept" --turns 5

# Generate new game concepts
python swarm/concept_agent.py "Your concept idea"
```

## Getting Started

1. Clone this repository:
```bash
git clone https://github.com/yourusername/living_game.git
cd living_game
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game selector:
```bash
python main.py
```

## Project Structure

```
living_game/
├── templates/
│   ├── vertical-jumper/
│   ├── top-down-rpg/
│   ├── shooter/
├── swarm/
│   ├── agent.py
│   ├── designer_agent.py
│   ├── developer_agent.py
│   └── concept_agent.py
├── architecture.excalidraw.svg
├── requirements.txt
└── main.py
```

## Contributing

Feel free to contribute by:
1. Adding new game templates
2. Improving existing templates
3. Enhancing documentation
4. Reporting issues
5. Extending the swarm agent system

## License

This project is open source and available under the MIT License.