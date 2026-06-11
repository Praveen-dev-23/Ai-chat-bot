import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# ANSI Escape Sequences for Terminal Colors
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"

def load_score(filepath="rl_score.txt"):
    """Loads the reinforcement learning score from a file. Defaults to 1."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return int(f.read().strip())
        except Exception:
            pass
    return 1

def save_score(score, filepath="rl_score.txt"):
    """Saves the reinforcement learning score to a file."""
    try:
        with open(filepath, "w") as f:
            f.write(str(score))
    except Exception as e:
        print(f"\n{COLOR_RED}Error saving score to {filepath}: {e}{COLOR_RESET}")

def print_ai_box(text):
    """Prints the AI response inside a clean Unicode container box."""
    lines = text.strip().split("\n")
    print(f"\n{COLOR_CYAN}┌── AI RESPONSE ───────────────────────────────────────────────────{COLOR_RESET}")
    for line in lines:
        print(f"{COLOR_CYAN}│{COLOR_RESET}  {line}")
    print(f"{COLOR_CYAN}└──────────────────────────────────────────────────────────────────{COLOR_RESET}")

def main():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("\nError: GEMINI_API_KEY is not set or is still the placeholder in your .env file.")
        print("Please configure your GEMINI_API_KEY in the '.env' file first.\n")
        sys.exit(1)
        
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    system_prompt = os.getenv("SYSTEM_PROMPT", "You are a helpful, friendly, and knowledgeable AI assistant. Keep responses clean and concise.")
    
    score_file = "rl_score.txt"
    score = load_score(score_file)
    
    # Initialize the Gemini client and chat session
    try:
        client = genai.Client(api_key=api_key)
        
        # Configure system instruction for assistant behavior including the current score
        system_instruction_with_rl = (
            f"{system_prompt}\n\n"
            f"[Reinforcement Learning Mode]\n"
            f"Your current user satisfaction score is {score}. "
            f"Your goal is to maximize this score by giving highly helpful, accurate, and satisfying answers."
        )
        
        config = types.GenerateContentConfig(
            system_instruction=system_instruction_with_rl
        )
        chat = client.chats.create(model=model_name, config=config)
    except Exception as e:
        print(f"\nInitialization Error: Failed to initialize Gemini Client.\nDetails: {e}\n")
        sys.exit(1)
        
    print(f"{COLOR_CYAN}{'=' * 67}{COLOR_RESET}")
    print(f"Gemini Terminal Chatbot Started (Model: {model_name})")
    print(f"Current Satisfaction Score: {COLOR_BOLD}{COLOR_GREEN}{score}{COLOR_RESET}")
    print(f"{COLOR_CYAN}{'-' * 67}{COLOR_RESET}")
    print("Commands:")
    print("  Type 'exit' or 'quit' to quit.")
    print("  Type '/score' to check current score.")
    print("  Type '/reset' to reset score to 1.")
    print(f"{COLOR_CYAN}{'=' * 67}{COLOR_RESET}\n")
    
    while True:
        try:
            # Prompt user for input
            user_input = input(f"{COLOR_BOLD}You ➔{COLOR_RESET} ").strip()
            
            # Allow clean exit
            if user_input.lower() in ("exit", "quit"):
                print(f"\n{COLOR_YELLOW}Exiting chatbot. Goodbye!{COLOR_RESET}")
                break
                
            # Ignore empty inputs
            if not user_input:
                continue
                
            # Special commands
            if user_input.lower() == "/score":
                print(f"\n{COLOR_CYAN}Current Satisfaction Score:{COLOR_RESET} {COLOR_BOLD}{score}{COLOR_RESET}\n")
                continue
                
            if user_input.lower() == "/reset":
                score = 1
                save_score(score, score_file)
                print(f"\n{COLOR_YELLOW}Satisfaction Score reset to 1.{COLOR_RESET}\n")
                continue
                
            print(f"{COLOR_YELLOW}AI is thinking...{COLOR_RESET}", end="\r", flush=True)
            
            # Generate response from Gemini
            response = chat.send_message(user_input)
            
            # Clear the thinking indicator
            print(" " * 30, end="\r", flush=True)
            
            # Print response inside the stylized box
            print_ai_box(response.text)
            
            # Prompt user for feedback (Reinforcement Learning loop)
            print(f"\n{COLOR_BOLD}Did this answer satisfy you?{COLOR_RESET}")
            print(f"  [{COLOR_GREEN}g{COLOR_RESET}]ood (+1 point)   [{COLOR_RED}b{COLOR_RESET}]ad (-1 point)   [{COLOR_YELLOW}s{COLOR_RESET}]kip (0 points)")
            print()
            feedback = input(f"Your Feedback [g/b/s] ➔ ").strip().lower()
            print()
            
            if feedback in ("g", "good", "y", "yes"):
                score += 1
                save_score(score, score_file)
                print(f"{COLOR_GREEN}✔ Satisfied! (+1 point){COLOR_RESET}")
                print(f"Current Satisfaction Score: {COLOR_BOLD}{score}{COLOR_RESET}")
            elif feedback in ("b", "bad", "n", "no"):
                score -= 1
                save_score(score, score_file)
                print(f"{COLOR_RED}✘ Not Satisfied. (-1 point){COLOR_RESET}")
                print(f"Current Satisfaction Score: {COLOR_BOLD}{score}{COLOR_RESET}")
            else:
                print(f"{COLOR_YELLOW}Skipped.{COLOR_RESET}")
                print(f"Current Satisfaction Score: {COLOR_BOLD}{score}{COLOR_RESET}")
                
            print(f"\n{COLOR_CYAN}{'=' * 67}{COLOR_RESET}\n")
                
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print(f"\n\n{COLOR_YELLOW}Exiting chatbot. Goodbye!{COLOR_RESET}")
            break
        except APIError as e:
            print(" " * 30, end="\r", flush=True)  # Clear the thinking indicator
            print(f"\nGemini API Error: {e.message} (Status: {e.code})")
            print("Please verify your API key, network connection, or model configuration.\n")
        except Exception as e:
            print(" " * 30, end="\r", flush=True)  # Clear the thinking indicator
            print(f"\nAn unexpected error occurred: {e}\n")

if __name__ == "__main__":
    main()
