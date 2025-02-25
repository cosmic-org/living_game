import argparse
from concept_agent_v2 import GameConceptGenerator
import logging

logger = logging.getLogger(__name__)

class CombinationAgent:
    def __init__(self):
        self.concept_generator = GameConceptGenerator()
        
    def combine_templates(self, template1: str, template2: str) -> str:
        """
        Combines two game templates to create a new hybrid concept.
        
        Args:
            template1: Path to the first template JSON file
            template2: Path to the second template JSON file
            
        Returns:
            str: Name of the generated combined concept file
        """
        try:
            # Generate a combined concept name
            combined_name = f"{template1.split('/')[-1].split('.')[0]}_{template2.split('/')[-1].split('.')[0]}_hybrid"
            
            # Generate a new game description using the concept generator
            prompt = f"Create a new game concept that combines elements from {template1} and {template2}"
            description = self.concept_generator.generate_game_description(prompt)
            
            # Save the combined concept
            output_file = self.concept_generator.save_description(combined_name, description)
            logger.info(f"Successfully created combined concept: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error combining templates: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Combine two game templates to create a new concept')
    parser.add_argument('template1', type=str, help='Path to the first template JSON file')
    parser.add_argument('template2', type=str, help='Path to the second template JSON file')
    
    args = parser.parse_args()
    
    combiner = CombinationAgent()
    try:
        output_file = combiner.combine_templates(args.template1, args.template2)
        print(f"\nSuccessfully created combined concept: {output_file}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 