import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

class GameConceptGenerator:
    def __init__(self):
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
    def sanitize_concept_name(self, concept):
        """Convert concept to a valid filename by removing special characters and converting to lowercase."""
        return re.sub(r'[^a-z0-9-]', '-', concept.lower()).strip('-')
    
    def generate_game_description(self, concept):
        """Generate a detailed game description using Claude 3.7."""
        prompt = f"""Given the game concept "{concept}", generate a detailed game description in JSON format.
        Focus only on gameplay mechanics and screen ifno, no story elements.
        The JSON should follow this structure:
        {{
            "gameTitle": "Unique name for the game",
            "genre": "Main genre of the game",
            "description": "Brief overview of the game concept",
            
            "coreMechanics": {{
                // Detailed breakdown of main gameplay mechanics
                // Include specific mechanics, rules, and interactions
            }},
            
            "features": {{
                "gameElements": {{
                    // List of main game elements and their properties
                }},
                // Other key features and systems
            }},
            
            "progression": {{
                // How the game progresses
                // Level structure, difficulty curve, etc.
            }},
            
            "visualStyle": {{
                "theme": "Overall visual theme",
                "artStyle": "Specific art style description",
                "animations": {{
                    // Key animation descriptions
                }}
            }},
            
            "audio": {{
                "music": "Music style description",
                "soundEffects": {{
                    // Key sound effect descriptions
                }}
            }},
            
            "monetization": {{
                "primary": "Main monetization strategy",
                "elements": [
                    // List of monetizable elements
                ]
            }},
            
            "uniqueSellingPoints": [
                // List of what makes the game unique
            ]
        }}

        Please ensure the JSON is properly formatted and focuses on concrete gameplay and visual elements rather than narrative elements.
        """
        
        try:
            response = self.anthropic.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=2000,
                temperature=0.7,
                system="You are a creative game design expert who specializes in generating detailed game concepts with a focus on mechanics and visual elements.",
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract JSON from the response
            content = response.content[0].text
            # Find JSON content between triple backticks if present
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            # Parse the JSON to validate it
            game_description = json.loads(content)
            return game_description
            
        except Exception as e:
            print(f"Error generating game description: {str(e)}")
            return None
    
    def save_description(self, concept, description):
        """Save the game description to a JSON file in the templates directory."""
        if description is None:
            return False
            
        # Sanitize concept name for directory
        dirname = self.sanitize_concept_name(concept)
        
        # Create templates/concept_name directory if it doesn't exist
        concept_dir = os.path.join("templates", dirname)
        os.makedirs(concept_dir, exist_ok=True)
        
        # Save as concept.json in the concept directory
        filepath = os.path.join(concept_dir, "concept.json")
        
        try:
            with open(filepath, 'w') as f:
                json.dump(description, f, indent=2)
            print(f"Game description saved to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving game description: {str(e)}")
            return False

def main():
    generator = GameConceptGenerator()
    
    # Get game concept from command line argument or user input
    import sys
    if len(sys.argv) > 1:
        concept = " ".join(sys.argv[1:])
    else:
        concept = input("Enter your game concept: ")
    
    # Generate and save the game description
    description = generator.generate_game_description(concept)
    if description:
        generator.save_description(concept, description)
    else:
        print("Failed to generate game description.")

if __name__ == "__main__":
    main() 