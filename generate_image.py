import os
import sys
from dotenv import load_dotenv
from huggingface_hub import InferenceClient, login
from requests.exceptions import RequestException
import time

# Load environment variables
load_dotenv()

# Get token from environment variable
token = os.getenv("HUGGINGFACE_TOKEN")
if not token:
    raise ValueError("Please set HUGGINGFACE_TOKEN in your .env file")

try:
    print("Logging in to Hugging Face...")
    login(token=token)
    
    print("Initializing client...")
    client = InferenceClient(
        model="gokaygokay/Flux-2D-Game-Assets-LoRA",
    )

    # Get prompt from user
    prompt = input("Enter your image prompt: ")
    
    print("Generating image... (this may take a few moments)")
    try:
        # output is a PIL.Image object
        image = client.text_to_image(
            "GRPZA, " + prompt + ", transparent background, game asset, pixel art",
            model="gokaygokay/Flux-2D-Game-Assets-LoRA"
        )

        # Create output filename based on prompt
        filename = f"{prompt.lower().replace(' ', '_')[:50]}.png"
        print("Saving image...")
        image.save(filename)
        print(f"✅ Image successfully saved as: {filename}")
        
    except RequestException as e:
        print(f"❌ Error generating image: {str(e)}")
        print("Please try again. If the problem persists, check your internet connection.")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ An unexpected error occurred: {str(e)}")
    sys.exit(1)