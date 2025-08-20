# app.py

import streamlit as st
from main_agent import ProtoForgeAgent

# --- Helper Functions (for better organization) ---

def load_css(file_name):
    """Loads a CSS file and injects it into the Streamlit app."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found: {file_name}. Please check the file path.")

def initialize_session_state():
    """Initializes all necessary session state variables if they don't exist."""
    if 'step' not in st.session_state:
        st.session_state.step = 0
        st.session_state.user_inputs = {}
        st.session_state.chat_history = []
        st.session_state.generating = False
        st.session_state.plan = ""

def handle_chat_flow():
    """Manages the step-by-step conversation with the user."""
    # This dictionary maps each step to a question and a key for storing the answer.
    chat_steps = {
        0: ("Hello! To begin, what is the **core objective** of your project?", "objective"),
        1: ("Interesting! What's your estimated **budget** for components?", "budget"),
        2: ("Do you have a preferred **microcontroller**?", "microcontroller"),
        3: ("What is your technical **skill level**?", "user_level"),
        4: ("Last question: Any **additional features** or constraints?", "additional_info"),
    }

    current_step = st.session_state.step
    if current_step in chat_steps:
        question, key = chat_steps[current_step]
        st.chat_message("assistant", avatar="🤖").write(question)
        if prompt := st.chat_input("Your response..."):
            st.session_state.user_inputs[key] = prompt
            st.session_state.chat_history.append({"role": "user", "content": prompt, "avatar": "👤"})
            st.session_state.step += 1
            st.rerun()

    elif current_step == 5:
        st.chat_message("assistant", avatar="🤖").write("Excellent! All inputs received. I'm ready to forge the initial project brief.")
        if st.button("✨ Generate Initial Plan", type="primary"):
            st.session_state.generating = True
            st.rerun()

def trigger_agent_generation():
    """Consolidates user inputs and calls the backend agent to generate the plan."""
    with st.spinner("The Master Planner is structuring your idea..."):
        full_concept = (
            f"Objective: {st.session_state.user_inputs.get('objective')}. "
            f"Budget: {st.session_state.user_inputs.get('budget')}. "
            f"Microcontroller: {st.session_state.user_inputs.get('microcontroller')}. "
            f"Skill Level: {st.session_state.user_inputs.get('user_level')}. "
            f"Additional Info: {st.session_state.user_inputs.get('additional_info')}."
        )
        try:
            planner = ProtoForgeAgent()
            initial_plan = planner.generate_initial_plan(full_concept)
            st.session_state.plan = initial_plan
        except Exception as e:
            st.session_state.plan = f"### An Error Occurred\n**Please check your terminal for details.**\n*Common issues include missing API keys in the `.env` file.*\n\n**Error details:**\n```\n{e}\n```"
        
        st.session_state.generating = False
        st.session_state.step = 6
        st.rerun()

# --- Main Application Logic ---

def main():
    """The main function that runs the Streamlit application."""
    st.set_page_config(page_title="ProtoForge AI", page_icon="🛠️", layout="centered")
    load_css("style.css")
    initialize_session_state()

    st.title("🛠️ ProtoForge AI")
    st.markdown("Your personal AI hardware architect. Let's start by defining your concept.")
    st.markdown("---")

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(name=message["role"], avatar=message.get("avatar")):
            st.markdown(message["content"])

    # Handle the current step of the app
    if st.session_state.step < 6:
        handle_chat_flow()
    
    if st.session_state.generating:
        trigger_agent_generation()
    
    if st.session_state.step == 6:
        st.success("The initial project brief is ready!")
        st.subheader("Generated Project Brief")
        st.markdown(st.session_state.plan, unsafe_allow_html=True)

if __name__ == "__main__":
    main()