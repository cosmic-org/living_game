import os
import json
import re
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GameDeveloper:
    def __init__(self):
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
    def load_concept(self, template_name):
        """Load the concept.json file from the specified template."""
        concept_path = os.path.join("templates", template_name, "concept.json")
        try:
            with open(concept_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading concept file: {str(e)}")
            return None
            
    def generate_game_code(self, concept):
        """Generate the game implementation based on the concept."""
        prompt = f"""Given this game concept in JSON format:
        {json.dumps(concept, indent=2)}
        
        Create a complete implementation of the game using Pygame. The implementation should:
        1. Follow the core mechanics and features described in the concept
        2. Use Pygame for graphics and input handling
        3. Include all necessary classes and functions
        4. Have proper game states (menu, playing, game over, etc.)
        5. Include comments explaining the code
        6. Handle window creation, event loop, and game loop
        7. Include proper error handling and cleanup
        8. Don't create sprites or sound effects, just use the default Pygame ones
        
        The code should be complete and runnable. Include all necessary imports and constants.
        Focus on implementing the core mechanics first, then add visual polish and additional features.
        
        Return ONLY the Python code, properly formatted and ready to be saved as main.py.
        """
        
        try:
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.7,
                system="You are an expert game developer specializing in Pygame implementations. Generate complete, working game code that follows best practices and implements the specified concept.",
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract code from the response
            content = response.content[0].text
            # Find code content between triple backticks if present
            code_match = re.search(r'```python\n(.*?)\n```', content, re.DOTALL)
            if code_match:
                content = code_match.group(1)
            return content
            
        except Exception as e:
            print(f"Error generating game code: {str(e)}")
            return None
    
    def save_implementation(self, template_name, code):
        """Save the generated code as main.py in the template directory."""
        if code is None:
            return False
            
        filepath = os.path.join("templates", template_name, "main.py")
        try:
            with open(filepath, 'w') as f:
                f.write(code)
            print(f"Game implementation saved to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving game implementation: {str(e)}")
            return False

def main():
    developer = GameDeveloper()
    
    # Get template name from command line argument or user input
    import sys
    if len(sys.argv) > 1:
        template_name = sys.argv[1]
    else:
        template_name = input("Enter the template name: ")
    
    # Load the concept
    concept = developer.load_concept(template_name)
    if not concept:
        print("Failed to load concept.")
        return
    
    # Generate and save the implementation
    code = developer.generate_game_code(concept)
    if code:
        developer.save_implementation(template_name, code)
    else:
        print("Failed to generate game implementation.")

if __name__ == "__main__":
    main() 