# main_agent.py

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# Set the correct environment variable
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro-latest",
    verbose=True,
    temperature=0.7 # Adjust for more creative/structured output
)

class ProtoForgeAgent:
    """
    This class orchestrates the initial planning phase.
    It takes raw user input and uses a Master Planner agent (powered by Gemini 1.5 Pro) to structure it.
    """
    def generate_initial_plan(self, user_prompt):
        """
        Uses a single agent to process the user's answers and create a structured brief.
        """
        print("[DEBUG] Initializing Master Planner Agent with Gemini 2.5 Pro...")

        
        master_planner = Agent(
            role='Master Hardware Project Planner',
            goal='Synthesize raw user requirements for a hardware project into a clear, structured, and concise project brief. The brief should be well-organized and easy for other agents to understand.',
            backstory='You are the lead project manager at a top hardware incubator. You excel at translating scattered ideas into a concrete and actionable starting plan. You always format your output in clean Markdown.',
            llm=llm,  # <-- Pass the configured Gemini model here
            verbose=True
        )

        # 2. DEFINE THE PLANNING TASK (This remains unchanged)
        planning_task = Task(
            description=f"Take the following user inputs and transform them into a structured project brief. The user's raw input is: '{user_prompt}'.",
            agent=master_planner,
            expected_output="""
            A well-formatted Markdown document with the following sections:
            - **Project Title:** A creative and descriptive name for the project.
            - **Objective:** A clear, one-sentence summary of what the project does.
            - **Key Features:** A bulleted list of the 3-5 primary features derived from the user's input.
            - **Core Components:** A preliminary list of required components based on the user's preferred microcontroller and objective.
            - **Constraints:** A bulleted list outlining the budget, user skill level, and any other limitations mentioned.
            """
        )

        # 3. CREATE AND RUN THE SINGLE-AGENT CREW (This remains unchanged)
        planning_crew = Crew(
            agents=[master_planner],
            tasks=[planning_task],
            verbose=2
        )

        # 4. KICK OFF THE TASK AND RETURN THE RESULT
        plan_result = planning_crew.kickoff()
        return plan_result