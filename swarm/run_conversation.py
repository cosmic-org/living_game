import argparse
import time
import logging
from designer_agent import DesignerAgent
from developer_agent import DeveloperAgent

logger = logging.getLogger(__name__)

def run_conversation(agent1, agent2, turns: int, initial_prompt: str):
    logger.info(f"Starting conversation with initial prompt: {initial_prompt}")
    current_message = initial_prompt
    
    for i in range(turns):
        logger.info(f"\nStarting turn {i+1}")
        print(f"\n--- Turn {i+1} ---")
        
        # Agent 1's turn
        print(f"\n{agent1.name} is thinking...")
        response1 = agent1.respond(current_message)
        print(f"{agent1.name}: {response1}")
        time.sleep(1)
        
        # Agent 2's turn
        print(f"\n{agent2.name} is thinking...")
        response2 = agent2.respond(response1)
        print(f"{agent2.name}: {response2}")
        time.sleep(1)
        
        current_message = response2

def main():
    parser = argparse.ArgumentParser(description='Run a conversation between two AI agents')
    parser.add_argument('--prompt', type=str, 
                       default="Let's create a simple text-based game. What kind of game should we make?",
                       help='The initial prompt to start the conversation')
    parser.add_argument('--turns', type=int, default=5,
                       help='Number of conversation turns')
    args = parser.parse_args()

    designer = DesignerAgent()
    developer = DeveloperAgent()
    
    print("Starting conversation between Game Designer and Developer...")
    run_conversation(designer, developer, turns=args.turns, initial_prompt=args.prompt)

if __name__ == "__main__":
    main() 