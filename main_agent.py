# main_agent.py

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from your .env file
load_dotenv()

class ProtoForgeAgent:
    def __init__(self):
        # This successfully reads the key from your .env file
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # If the key isn't found, it raises a clear error
            raise ValueError("FATAL ERROR: GEMINI_API_KEY not found in .env file. Please ensure the file exists and the variable name is correct.")
        
        # Configure the SDK with your key
        genai.configure(api_key=api_key)

        # Initialize the specific model you want to use
        # 'gemini-1.5-flash-latest' is a great, fast choice.
        self.model = genai.GenerativeModel("gemini-1.5-flash-latest")

    def generate_initial_plan(self, user_prompt: str) -> str:
        """
        Generates a structured project plan using the direct Gemini SDK.
        """
        print("[DEBUG] Running Master Planner (Direct SDK)...")

        # This is the prompt that instructs the AI on how to format the output
        prompt = f"""
        You are an expert hardware project planner. Based on the following user input, create a structured project brief.
        The brief must have these exact Markdown sections:
        - **Project Title:**
        - **Objective:**
        - **Key Features:**
        - **Core Components:**
        - **Constraints:**

        User Input: {user_prompt}
        """

        try:
            # Make the API call to Google
            response = self.model.generate_content(prompt)
            # Return the text part of the response
            return response.text
        except Exception as e:
            # If anything goes wrong, return a clear error message
            return f"[ERROR] The call to the Gemini API failed: {e}"