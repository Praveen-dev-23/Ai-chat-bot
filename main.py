import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

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
    
    # Initialize the Gemini client and chat session
    try:
        client = genai.Client(api_key=api_key)
        
        # Configure system instruction for assistant behavior
        config = types.GenerateContentConfig(
            system_instruction=system_prompt
        )
        chat = client.chats.create(model=model_name, config=config)
    except Exception as e:
        print(f"\nInitialization Error: Failed to initialize Gemini Client.\nDetails: {e}\n")
        sys.exit(1)
        
    print("=" * 60)
    print(f"Gemini Terminal Chatbot Started (Model: {model_name})")
    print("Type 'exit' or press Ctrl+C to quit.")
    print("=" * 60)
    print()
    
    while True:
        try:
            # Prompt user for input
            user_input = input("You: ").strip()
            
            # Allow clean exit
            if user_input.lower() in ("exit", "quit"):
                print("\nExiting chatbot. Goodbye!")
                break
                
            # Ignore empty inputs
            if not user_input:
                continue
                
            print("AI is thinking...", end="\r", flush=True)
            
            # Generate response from Gemini
            response = chat.send_message(user_input)
            
            # Clear the thinking indicator
            print(" " * 20, end="\r", flush=True)
            
            # Print response cleanly
            print(f"AI: {response.text}")
            print()
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\nExiting chatbot. Goodbye!")
            break
        except APIError as e:
            print(" " * 20, end="\r", flush=True)  # Clear the thinking indicator
            print(f"\nGemini API Error: {e.message} (Status: {e.code})")
            print("Please verify your API key, network connection, or model configuration.\n")
        except Exception as e:
            print(" " * 20, end="\r", flush=True)  # Clear the thinking indicator
            print(f"\nAn unexpected error occurred: {e}\n")

if __name__ == "__main__":
    main()
