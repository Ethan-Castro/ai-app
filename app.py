#############################################
# Imports
#############################################
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from vertexai import init as vertexai_init
from vertexai.preview.language_models import ChatModel  # Optional for advanced chat
from vertexai.generation import Message  # For multi-turn, optional

import streamlit as st
from streamlit_chat import message
from streamlit.components.v1 import html

#############################################
# Vertex AI Initialization
#############################################
# Project and location settings
PROJECT_ID = "alison-apps"   # Your project ID
LOCATION = "us-central1"     # Your location

# Initialize Vertex AI with your project and location
vertexai_init(project=PROJECT_ID, location=LOCATION)

#############################################
# Model Configuration
#############################################
MODEL_ID = "gemini-2.0-flash-exp"  # Model to use, e.g., "gemini-pro"

# Optional: Large system prompt text (if needed as system instruction)
textsi_1 = """Welcoming & Offering Support Options APP
Welcome Message:
'Welcome to the YELLOW Mind Support Bot!' 
... (truncated for brevity) ...
"""

#############################################
# Chatbot Helper Functions
#############################################
def generate_response(user_input: str) -> str:
    """
    Takes user_input, sends it to the Gemini model, streams the output,
    and returns the concatenated final text.
    """
    try:
        # Initialize the model
        model = GenerativeModel(model_id=MODEL_ID)

        # Prepare user input as a Part object
        contents = [
            Part(text=user_input, mime_type="text/plain", role="user")
        ]

        # Stream the response
        response_it = model.generate_content(
            contents=contents,
            temperature=1.0,
            top_p=0.95,
            max_output_tokens=1024,
            stream=True
        )

        # Concatenate streamed chunks
        response_text = ""
        for chunk in response_it:
            response_text += chunk.text

        return response_text

    except Exception as e:
        return f"Error generating response: {e}"

#############################################
# Streamlit UI
#############################################
st.set_page_config(page_title="Bakersfield Adult School ChatBot",
                   page_icon="🤖",
                   layout="wide")

def user_prompt_submit():
    """
    Callback function when user hits 'Enter' in the text_input box.
    """
    user_input = st.session_state.input
    st.session_state.prompt = user_input
    st.session_state["input"] = ""

if "prompt" not in st.session_state:
    st.session_state.prompt = ""

# Display initial greeting 
message("Thank you for your interest in Bakersfield Adult School! What would you like to learn more about?",
        key="initial-bot-greeting")

# If the user has typed something, generate a response
if st.session_state.prompt:
    user_query = st.session_state.prompt
    user_response = generate_response(user_query)

    # Show user question
    message(user_query, is_user=True, avatar_style="adventurer", key="user-message")
    # Show bot response (or error)
    if user_response.startswith("Error"):
        st.error(user_response)
    else:
        message(user_response, key="bot-response")

# Text input at the bottom
st.text_input(
    key="input",
    on_change=user_prompt_submit,
    label="Type in your question here",
    label_visibility="hidden",
    placeholder="Type in your question here"
)

# Styling to keep the text input pinned to bottom
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

#############################################
# Optional: Demonstration function
#############################################
def generate_workflow_demo():
    """
    Demonstrates how you might stream a system-level prompt
    without user input. It references the Vertex GenerativeModel directly.
    """
    try:
        # Instantiate the model
        model = GenerativeModel(model_id=MODEL_ID)

        # Provide system instructions as a Part with role="system"
        contents = [
            Part(text=textsi_1, mime_type="text/plain", role="system")
        ]

        # Stream the model’s response
        response_it = model.generate_content(
            contents=contents,
            temperature=1.0,
            top_p=0.95,
            max_output_tokens=800,   # Adjust as needed
            stream=True             # Streaming enabled
        )

        for chunk in response_it:
            print(chunk.text, end="")
        print("\n\n--- End of streaming response ---")

    except Exception as e:
        print("Error in generate_workflow_demo:", str(e))

#############################################
# Optional: Uncomment to see system prompt streaming
#############################################
# generate_workflow_demo()
