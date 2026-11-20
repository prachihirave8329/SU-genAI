
import os
import uuid

import requests
import streamlit as st

st.title("Jan Aushadhi AI Assistant")
API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)

# Start a new conversation
def new_chat():

    st.session_state.messages = []
    st.session_state.pending_approval = False
    st.session_state.thread_id = str(uuid.uuid4())


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = False


# New chat button
if st.button("New Chat"):
    new_chat()
    st.rerun()


# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# Ask a question
question = st.chat_input(
    "Ask about Jan Aushadhi...",
    disabled=st.session_state.pending_approval
)

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    try:

        response = requests.post(
            API_URL + "/agent",
            json={
                "question": question,
                "thread_id": st.session_state.thread_id
            },
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        if data["status"] == "approval_required":

            st.session_state.pending_approval = True

        else:

            answer = data.get("answer", "No answer received.")

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

    except requests.exceptions.RequestException:

        st.session_state.messages.append({
            "role": "assistant",
            "content": "Unable to connect to the API. Please check FastAPI."
        })

    st.rerun()


# Human approval section
if st.session_state.pending_approval:

    st.warning("Human approval is required.")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Approve"):

            try:

                response = requests.post(
                    API_URL + "/agent/approval",
                    json={
                        "thread_id": st.session_state.thread_id,
                        "approved": True
                    },
                    timeout=60
                )

                response.raise_for_status()

                data = response.json()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data.get("answer", "No answer received.")
                })

                st.session_state.pending_approval = False

            except requests.exceptions.RequestException:

                st.error("Unable to connect to the API.")

            st.rerun()

    with col2:

        if st.button("Reject"):

            try:

                response = requests.post(
                    API_URL + "/agent/approval",
                    json={
                        "thread_id": st.session_state.thread_id,
                        "approved": False
                    },
                    timeout=60
                )

                response.raise_for_status()

                data = response.json()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data.get("answer", "No answer received.")
                })

                st.session_state.pending_approval = False

            except requests.exceptions.RequestException:

                st.error("Unable to connect to the API.")

            st.rerun()
