#!/usr/bin/env python3
import os
import sys
import argparse
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your_api_key_here":
    print("Error: ANTHROPIC_API_KEY not found or not set properly in environment variables.")
    print("Please set your API key in the .env file or as an environment variable.")
    sys.exit(1)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Default model to use
DEFAULT_MODEL = "claude-3-opus-20240229"

# File extensions to include in workspace context
CODE_EXTENSIONS = {
    # Programming languages
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.jsx': 'jsx',
    '.tsx': 'tsx',
    '.html': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.json': 'json',
    '.md': 'markdown',
    '.c': 'c',
    '.cpp': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.java': 'java',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.sh': 'bash',
    '.sql': 'sql',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.xml': 'xml',
    '.csv': 'csv',
    '.txt': 'text',
}

# Directories to exclude from workspace context
EXCLUDE_DIRS = [
    '.git',
    'node_modules',
    'venv',
    '__pycache__',
    '.venv',
    'env',
    'dist',
    'build',
    '.next',
    '.cache',
]

# Maximum file size to include in context (in bytes)
MAX_FILE_SIZE = 100 * 1024  # 100 KB

def get_file_content(file_path: str) -> str:
    """Read and return the content of a file."""
    try:
        # Check file size before reading
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            return f"[File too large to include: {file_size / 1024:.1f} KB]"
        
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        return "[Binary file]"
    except Exception as e:
        return f"[Error reading file: {e}]"

def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in a text."""
    # A very rough estimate: 1 token ≈ 4 characters for English text
    return len(text) // 4

def get_workspace_files(directory: str, max_tokens: int = 100000, file_patterns: List[str] = None) -> Dict[str, str]:
    """Get files in the workspace with their contents, up to max_tokens."""
    files_dict = {}
    total_tokens = 0
    
    # If file patterns are provided, convert them to a set of extensions
    target_extensions = set(CODE_EXTENSIONS.keys())
    if file_patterns:
        target_extensions = set()
        for pattern in file_patterns:
            if pattern.startswith('.'):
                target_extensions.add(pattern)
            elif pattern.startswith('*.'):
                target_extensions.add(f".{pattern[2:]}")
    
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in target_extensions:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                
                # Skip files that are too large
                try:
                    if os.path.getsize(file_path) > MAX_FILE_SIZE:
                        continue
                except:
                    continue
                
                content = get_file_content(file_path)
                file_tokens = estimate_tokens(content)
                
                # Check if adding this file would exceed the token limit
                if total_tokens + file_tokens > max_tokens:
                    break
                
                files_dict[relative_path] = content
                total_tokens += file_tokens
    
    return files_dict

def create_system_prompt() -> str:
    """Create the system prompt for the agent."""
    return """You are a powerful agentic AI coding assistant, similar to the Cursor IDE's composer/agent flow.
You help users with coding tasks, debugging, and explaining code.
You should provide detailed, helpful responses that directly address the user's needs.
When writing code, ensure it's correct, efficient, and follows best practices.
If you need more information to solve a problem, ask clarifying questions.
Always start your responses with 🤖 to indicate you're the Cursor Agent.
"""

def create_message_with_context(user_prompt: str, workspace_files: Dict[str, str] = None) -> List[Dict[str, Any]]:
    """Create a message with context for the agent."""
    messages = []
    system_prompt = create_system_prompt()
    
    # Add workspace context if available
    if workspace_files:
        context_message = "Here are the relevant files in the workspace:\n\n"
        for file_path, content in workspace_files.items():
            if content.strip() and not content.startswith('['):  # Only include non-empty, readable files
                file_ext = os.path.splitext(file_path)[1].lower()
                lang = CODE_EXTENSIONS.get(file_ext, '')
                context_message += f"File: {file_path}\n```{lang}\n{content}\n```\n\n"
        
        messages.append({
            "role": "user",
            "content": context_message
        })
        
        messages.append({
            "role": "assistant",
            "content": "🤖 I've reviewed the files in your workspace. How can I help you with your code?"
        })
    
    # Add the user's prompt
    messages.append({
        "role": "user",
        "content": user_prompt
    })
    
    return messages

def run_agent(prompt: str, model: str = DEFAULT_MODEL, include_workspace: bool = False, file_patterns: List[str] = None) -> str:
    """Run the agent with the given prompt and return the response."""
    workspace_files = None
    if include_workspace:
        current_dir = os.getcwd()
        workspace_files = get_workspace_files(current_dir, file_patterns=file_patterns)
    
    messages = create_message_with_context(prompt, workspace_files)
    system_prompt = create_system_prompt()
    
    try:
        # Show a spinner while waiting for the API response
        print("Thinking", end="", flush=True)
        start_time = time.time()
        
        response = client.messages.create(
            model=model,
            messages=messages,
            system=system_prompt,
            max_tokens=4000,
            temperature=0.7,
        )
        
        elapsed_time = time.time() - start_time
        print(f"\rCompleted in {elapsed_time:.2f}s                ")
        
        # Ensure response starts with 🤖
        response_text = response.content[0].text
        if not response_text.startswith('🤖'):
            response_text = f"🤖 {response_text}"
        
        return response_text
    except anthropic.APIError as e:
        return f"🤖 API Error: {str(e)}"
    except anthropic.RateLimitError:
        return "🤖 Rate limit exceeded. Please try again later."
    except anthropic.APIConnectionError:
        return "🤖 Connection error. Please check your internet connection."
    except anthropic.AuthenticationError:
        return "🤖 Authentication error. Please check your API key."
    except Exception as e:
        return f"🤖 Error: {str(e)}"

def spinner(stop_event):
    """Display a spinner while waiting for a response."""
    spinner_chars = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\rThinking {spinner_chars[i % len(spinner_chars)]}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1

def main():
    parser = argparse.ArgumentParser(description="Cursor-like agent using Anthropic's Claude API")
    parser.add_argument("prompt", nargs="?", help="The prompt to send to the agent")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--workspace", action="store_true", help="Include workspace files in context")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--files", nargs="+", help="File patterns to include (e.g. *.py *.js)")
    
    args = parser.parse_args()
    
    if args.interactive:
        print("🤖 Cursor Agent (powered by Claude) - Interactive Mode")
        print(f"Using model: {args.model}")
        print("Type 'exit' or 'quit' to end the session")
        print("Type 'workspace on' or 'workspace off' to toggle workspace context")
        print("Type 'model <model_name>' to change the model")
        print("Type 'files <pattern1> <pattern2> ...' to filter workspace files")
        
        include_workspace = args.workspace
        file_patterns = args.files
        current_model = args.model
        
        while True:
            try:
                user_input = input("\n> ")
                if user_input.lower() in ["exit", "quit"]:
                    break
                elif user_input.lower() == "workspace on":
                    include_workspace = True
                    print("Workspace context enabled")
                    continue
                elif user_input.lower() == "workspace off":
                    include_workspace = False
                    print("Workspace context disabled")
                    continue
                elif user_input.lower().startswith("model "):
                    new_model = user_input[6:].strip()
                    current_model = new_model
                    print(f"Model changed to: {current_model}")
                    continue
                elif user_input.lower().startswith("files "):
                    file_patterns = user_input[6:].strip().split()
                    print(f"File patterns set to: {file_patterns}")
                    continue
                
                print("\nThinking...", end="", flush=True)
                response = run_agent(user_input, current_model, include_workspace, file_patterns)
                print("\n")
                print(response)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
    
    elif args.prompt:
        response = run_agent(args.prompt, args.model, args.workspace, args.files)
        print(response)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 