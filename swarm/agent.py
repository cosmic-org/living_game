import anthropic
import logging
from typing import List
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMAgent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        
        # Load environment variables
        load_dotenv()
        
        # Get API key from .env file
        api_key = os.getenv('ANTHROPIC_API_KEY')
        logger.info(f"API Key found for {name}: {'Yes' if api_key else 'No'}")
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")
            
        self.client = anthropic.Anthropic(api_key=api_key)
        logger.info(f"Successfully created Anthropic client for {self.name}")
        self.conversation_history: List[str] = []
    
    def respond(self, message: str) -> str:
        try:
            # Add the incoming message to conversation history
            self.conversation_history.append(f"Other: {message}")
            
            # Construct the full conversation context
            conversation_context = "\n".join(self.conversation_history[-4:])
            
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=400,
                system=f"{self.system_prompt} Keep responses under 3 sentences when possible.",
                messages=[
                    {
                        "role": "user",
                        "content": f"Here is the recent conversation:\n{conversation_context}\n\nPlease provide your next response:"
                    }
                ]
            )
            
            # Add own response to history
            self.conversation_history.append(f"{self.name}: {response.content}")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in respond method: {str(e)}")
            raise