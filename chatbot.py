import streamlit as st
from streamlit_chat import message
import openai
import time
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# ============ CONFIG =============
load_dotenv(".env")
openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")  # Replace with your actual Assistant ID
# ==================================

# Initialize session state for chat management
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    # Create first chat
    chat_id = f"chat_{int(time.time())}"
    st.session_state.current_chat_id = chat_id
    st.session_state.chats[chat_id] = {
        "name": "New Chat",
        "thread_id": openai.beta.threads.create().id,
        "messages": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

# Set page config
st.set_page_config(
    page_title="Insurance Chatbot", 
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
    }
    .welcome-message {
        text-align: center;
        padding: 2rem;
        margin: 2rem 0;
        background-color: #f0f2f6;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .sidebar-chat-item {
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        cursor: pointer;
        border: 1px solid #e0e0e0;
    }
    .sidebar-chat-item:hover {
        background-color: #f0f2f6;
    }
    .sidebar-chat-item.active {
        background-color: #e8f4f8;
        border-color: #1f77b4;
    }
    .sidebar-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    .sidebar-header img {
        margin-right: 15px;
    }
    .sidebar-header h2 {
        margin: 0;
        font-size: 1.2rem;
        color: #1f77b4;
    }
    /* Fix for streamlit-chat message alignment */
    .stChatMessage {
        align-items: flex-start !important;
    }
    .stChatMessage > div {
        align-items: flex-start !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for chat management
with st.sidebar:
    # Title and logo in sidebar
    st.markdown("""
    <div class="sidebar-header">
        <img src="https://raw.githubusercontent.com/Shuaib21803/insurance-assistant/refs/heads/main/static/insurance-logo.png" width="60">
        <h2>Insurance Policy Assistant</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # New Chat button
    if st.button("➕ New Chat", use_container_width=True):
        new_chat_id = f"chat_{int(time.time())}"
        st.session_state.chats[new_chat_id] = {
            "name": "New Chat",
            "thread_id": openai.beta.threads.create().id,
            "messages": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.current_chat_id = new_chat_id
        st.rerun()
    
    st.divider()
    st.subheader("Recent Chats")
    
    # Display existing chats in descending order (latest first)
    sorted_chats = sorted(
        st.session_state.chats.items(), 
        key=lambda x: x[1]['created_at'], 
        reverse=True
    )
    
    for chat_id, chat_data in sorted_chats:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Chat selection button
            if st.button(
                f"{chat_data['name']}", 
                key=f"select_{chat_id}",
                use_container_width=True,
                type="primary" if chat_id == st.session_state.current_chat_id else "secondary"
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        
        with col2:
            # Delete button
            if st.button("🗑", key=f"delete_{chat_id}", help="Delete chat"):
                if len(st.session_state.chats) > 1:  # Don't delete if it's the only chat
                    del st.session_state.chats[chat_id]
                    if chat_id == st.session_state.current_chat_id:
                        # Switch to another chat if current is deleted
                        st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                    st.rerun()
                else:
                    st.warning("🚫")

# Main chat area
current_chat = st.session_state.chats[st.session_state.current_chat_id]

# Chat input
user_input = st.chat_input("Ask me anything about your insurance policy...")

# Welcome message for new chats (only show if no messages)
if not current_chat["messages"] and not user_input:
    st.markdown("""
    <div class="welcome-message">
        <h3>👋 Welcome to your Insurance Assistant!</h3>
        <p>I'm here to help you understand your insurance policies, claims, and coverage details. Simply ask me any questions about your insurance!</p>
    </div>
    """, unsafe_allow_html=True)

# Chat containera
with st.container():
    # Render chat history
    for i, msg in enumerate(current_chat["messages"]):
        message(
            msg["content"], 
            is_user=(msg["role"] == "user"), 
            key=f"{st.session_state.current_chat_id}_{i}",
            avatar_style=None if msg["role"] == "user" else "bottts",
            logo = "https://raw.githubusercontent.com/Shuaib21803/insurance-assistant/refs/heads/main/static/user-logo.png" if msg["role"] == "user" else None,
            seed=123 if msg["role"] == "user" else 456
        )

if user_input:
    # Update chat name based on first message
    if not current_chat["messages"]:
        # Generate a short name from the first message
        chat_name = user_input[:30] + "..." if len(user_input) > 30 else user_input
        st.session_state.chats[st.session_state.current_chat_id]["name"] = chat_name
        # Update created_at to current time for proper sorting
        st.session_state.chats[st.session_state.current_chat_id]["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add user message to chat and update session state immediately
    current_chat["messages"].append({"role": "user", "content": user_input})
    st.session_state.chats[st.session_state.current_chat_id] = current_chat
    
    # Display the user message immediately
    message(
        user_input, 
        is_user=True, 
        key=f"{st.session_state.current_chat_id}_{len(current_chat['messages'])-1}",
        logo="https://raw.githubusercontent.com/Shuaib21803/insurance-assistant/refs/heads/main/static/user-logo.png",
        seed=123
    )
    
    # Send message to thread
    openai.beta.threads.messages.create(
        thread_id=current_chat["thread_id"],
        role="user",
        content=user_input
    )

    # Run assistant
    run = openai.beta.threads.runs.create(
        thread_id=current_chat["thread_id"],
        assistant_id=ASSISTANT_ID,
    )

    # Poll for completion
    with st.spinner("Thinking..."):
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=current_chat["thread_id"],
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                st.error("The assistant failed to respond.")
                break
            time.sleep(1)

    # Get assistant reply
    messages = openai.beta.threads.messages.list(thread_id=current_chat["thread_id"])
    assistant_message = next(
        (msg for msg in messages.data if msg.role == "assistant"), None
    )

    if assistant_message:
        reply = assistant_message.content[0].text.value
        current_chat["messages"].append({"role": "assistant", "content": reply})
        
        # Display assistant message immediately
        message(
            reply, 
            is_user=False, 
            key=f"{st.session_state.current_chat_id}_{len(current_chat['messages'])-1}",
            avatar_style="bottts",
            seed=456
        )

    # Update session state and rerun
    st.session_state.chats[st.session_state.current_chat_id] = current_chat
    st.rerun()