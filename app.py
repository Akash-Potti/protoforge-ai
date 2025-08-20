# app.py

import streamlit as st
from main_agent import ProtoForgeAgent

# --- Helper Function to Load CSS ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- Page Configuration (must be the first Streamlit command) ---
st.set_page_config(
    page_title="ProtoForge AI",
    page_icon="🛠️",
    layout="centered"
)

# --- Load Custom CSS for the sleek theme ---
load_css("style.css")

# --- Initialize Session State for the conversation ---
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.user_inputs = {}
    st.session_state.chat_history = []
    st.session_state.generating = False
    st.session_state.plan = ""

# --- App Header ---
st.title("🛠️ ProtoForge AI")
st.markdown("Your personal AI hardware architect. Let's start by defining your concept.")
st.markdown("---")

# --- Display Chat History ---
if st.session_state.step < 6:
    for message in st.session_state.chat_history:
        with st.chat_message(name=message["role"], avatar=message.get("avatar")):
            st.markdown(message["content"])

# --- The Manual, Scripted Chatbot Flow ---
if st.session_state.step == 0:
    st.chat_message("assistant", avatar="🤖").write("Hello! To begin, what is the **core objective** of your project?")
    if prompt := st.chat_input("What do you want to build?"):
        st.session_state.user_inputs['objective'] = prompt
        st.session_state.chat_history.append({"role": "user", "content": prompt, "avatar": "👤"})
        st.session_state.step = 1
        st.rerun()
elif st.session_state.step == 1:
    st.chat_message("assistant", avatar="🤖").write("Interesting! What's your estimated **budget** for components?")
    if prompt := st.chat_input("e.g., 'Under $100', 'Flexible'"):
        st.session_state.user_inputs['budget'] = prompt
        st.session_state.chat_history.append({"role": "user", "content": prompt, "avatar": "👤"})
        st.session_state.step = 2
        st.rerun()
elif st.session_state.step == 2:
    st.chat_message("assistant", avatar="🤖").write("Do you have a preferred **microcontroller**?")
    if prompt := st.chat_input("e.g., 'ESP32', 'Arduino Uno', or 'No preference'"):
        st.session_state.user_inputs['microcontroller'] = prompt
        st.session_state.chat_history.append({"role": "user", "content": prompt, "avatar": "👤"})
        st.session_state.step = 3
        st.rerun()
elif st.session_state.step == 3:
    st.chat_message("assistant", avatar="🤖").write("What is your technical **skill level**?")
    if prompt := st.chat_input("e.g., 'Beginner', 'Intermediate', 'Advanced'"):
        st.session_state.user_inputs['user_level'] = prompt
        st.session_state.chat_history.append({"role": "user", "content": prompt, "avatar": "👤"})
        st.session_state.step = 4
        st.rerun()
elif st.session_state.step == 4:
    st.chat_message("assistant", avatar="🤖").write("Last question: Any **additional features** or constraints?")
    if prompt := st.chat_input("e.g., 'Must be portable', 'Needs WiFi', or 'N/A'"):
        st.session_state.user_inputs['additional_info'] = prompt
        st.session_state.chat_history.append({"role": "user", "content": prompt, "avatar": "👤"})
        st.session_state.step = 5
        st.rerun()
elif st.session_state.step == 5:
    st.chat_message("assistant", avatar="🤖").write("Excellent! All inputs received. I'm ready to forge the initial project brief.")
    if st.button("✨ Generate Initial Plan", type="primary"):
        st.session_state.generating = True
        st.rerun()

# --- Backend Trigger and Result Display ---
if st.session_state.generating:
    with st.spinner("The Master Planner is structuring your idea..."):
        # Combine all user inputs into a single, clean prompt
        full_concept = " ".join(f"{k}: {v}." for k, v in st.session_state.user_inputs.items())
        
        try:
            # Instantiate and call the backend
            planner = ProtoForgeAgent()
            initial_plan = planner.generate_initial_plan(full_concept)
            st.session_state.plan = initial_plan
        except Exception as e:
            # Catch potential errors (like a missing API key) and display them
            st.session_state.plan = f"### An Error Occurred\n**Please check your terminal for details.**\n\n**Error details:**\n```\n{e}\n```"
        
        st.session_state.generating = False
        st.session_state.step = 6
        st.rerun()

if st.session_state.step == 6:
    st.success("The initial project brief is ready!")
    st.subheader("Generated Project Brief")
    st.markdown(st.session_state.plan, unsafe_allow_html=True)