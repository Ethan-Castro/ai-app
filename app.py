from google import genai
from google.genai import types
import streamlit as st
from streamlit_chat import message
from streamlit.components.v1 import html

# Configuration
project_id = "alisons-apps"
location = "us-central1"
model_name = "gemini-2.0-flash-exp"

def get_genai_client():
    try:
        return genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )
    except Exception as e:
        st.error("Failed to initialize GenAI client: " + str(e))
        return None

def generate_response(user_input):
    client = get_genai_client()
    if not client:
        return "Error initializing the GenAI client. Please check your configuration."

    contents = [
        types.Content(
            role="user",
            parts=[user_input]
        )
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
        ],
    )

    try:
        response_chunks = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=generate_content_config
        )
        response = "".join(chunk.text for chunk in response_chunks)
        return response
    except Exception as e:
        return "An error occurred while generating the response: " + str(e)

# Streamlit UI
st.set_page_config(page_title="Bakersfield Adult School ChatBot", page_icon="🤖", layout="wide")

def user_prompt_submit():
    user_input = st.session_state.input
    st.session_state.prompt = user_input
    st.session_state["input"] = ""

if "prompt" not in st.session_state:
    st.session_state.prompt = ""

message("Thank you for your interest in Bakersfield Adult School! What would you like to learn more about?", key="-1")

if st.session_state.prompt:
    user_query = st.session_state.prompt
    user_response = generate_response(user_query)
    if "Error" in user_response:
        st.error(user_response)
    else:
        message(user_query, is_user=True, avatar_style="adventurer", key="user_message")
        message(user_response, key="bot_response")

st.text_input(key="input",
              on_change=user_prompt_submit,
              label="Type in your question here",
              label_visibility="hidden",
              placeholder="Type in your question here")

styl = """
<style>
    .stTextInput {
        position: fixed;
        bottom: 10px;
        left: 0;
        right: 0;
        width: 96vw;
        margin: auto;
    }    

    .block-container {
        position: fixed !important;
        bottom: 1rem !important;
        padding: 0 !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        max-height: 90vh !important;
        width: 96vw !important;
    }

    #MainMenu {
        display: none;
    }

    footer {
        display: none;
    }
</style>
"""
st.markdown(styl, unsafe_allow_html=True)
