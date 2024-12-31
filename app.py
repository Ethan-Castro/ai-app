#############################################
# Imports
#############################################
from google.genai.model import GenerativeModel
from google.genai.config import GenerationConfig
from google.genai.safety import SafetyCategory
from google.genai.types import Content, Part

import streamlit as st
from streamlit_chat import message
from streamlit.components.v1 import html

#############################################
# Configuration
#############################################
MODEL_ID = "gemini-2.0-flash-exp"

#############################################
# Large system prompt text
#############################################
textsi_1 = """Welcoming & Offering Support Options APP
Welcome Message:
Start with a warm and friendly welcome message. For example: \"Welcome to the YELLOW Mind Support Bot! I’m glad to have you here on this journey towards an empowered and stress-free relationship with your body and food.\"
Introduction to Course:
Briefly introduce the purpose of the course and how the app will assist them. For example: \"This course is designed to support you in developing a positive body image and overcome disordered eating patterns. Our AI is here to guide you every step of the way.\"
Topic Selection Prompt:
Invite participants to choose a topic they would like support or guidance with...
[Truncated for brevity in this example, but keep your entire text here if needed]
"""

#############################################
# (Optional) Demonstration function
#############################################
def generate_workflow_demo():
    """
    Demonstrates how you can stream a response using a big system instruction
    (textsi_1) with the new GenerativeModel API.
    """
    gemini_model = GenerativeModel(model_id=MODEL_ID)

    # We can add a single system-level Content if we want the LLM
    # to always incorporate textsi_1 as a system prompt
    contents = [
        Content(
            role="system",
            parts=[Part(text=textsi_1)]
        )
        # We don't include user content here because this is a "demo" 
        # streaming the system content's output
    ]

    generation_config = GenerationConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=1807,
    )

    # Example safety settings
    safety_settings = {
        SafetyCategory.HATE_SPEECH: "OFF",
        SafetyCategory.DANGEROUS_CONTENT: "OFF",
        SafetyCategory.SEXUALLY_EXPLICIT: "OFF",
        SafetyCategory.HARASSMENT: "OFF",
    }

    try:
        # Stream the response
        model_response = gemini_model.generate_content(
            contents=contents,
            config=generation_config,
            safety_settings=safety_settings,
            stream=True
        )
        # Print streamed chunks to console (if your platform shows logs)
        for chunk in model_response:
            print(chunk.text, end="")
        print("\n\n--- End of streaming response ---")
    except Exception as e:
        print("Error in generate_workflow_demo:", str(e))

#############################################
# Chatbot Helper Functions
#############################################
def get_gemini_model():
    """
    Initializes and returns the GenerativeModel for Vertex AI.
    """
    try:
        gemini_model = GenerativeModel(model_id=MODEL_ID)
        return gemini_model
    except Exception as e:
        st.error("Failed to initialize the GenAI model: " + str(e))
        return None

def generate_response(user_input: str) -> str:
    """
    Handles conversation in the Streamlit chatbot context.
    Takes user_input from the text box, queries the LLM, and returns the response.
    """
    gemini_model = get_gemini_model()
    if not gemini_model:
        return "Error: Could not initialize the GenAI model."

    # Wrap user input in the new content format
    contents = [
        Content(
            role="user",
            parts=[Part(text=user_input)]
        )
    ]

    # If you want a system prompt alongside the user prompt, you'd do:
    # system_content = Content(role="system", parts=[Part(text=textsi_1)])
    # contents.insert(0, system_content)

    generation_config = GenerationConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
    )

    # Example safety settings
    safety_settings = {
        SafetyCategory.HATE_SPEECH: "OFF",
        SafetyCategory.DANGEROUS_CONTENT: "OFF",
        SafetyCategory.SEXUALLY_EXPLICIT: "OFF",
        SafetyCategory.HARASSMENT: "OFF",
    }

    try:
        # Stream the response
        model_response = gemini_model.generate_content(
            contents=contents,
            config=generation_config,
            safety_settings=safety_settings,
            stream=True
        )
        # Concatenate all streamed chunks
        response_text = ""
        for chunk in model_response:
            response_text += chunk.text
        return response_text
    except Exception as e:
        return "An error occurred while generating the response: " + str(e)

#############################################
# Streamlit UI
#############################################
st.set_page_config(page_title="Bakersfield Adult School ChatBot",
                   page_icon="🤖",
                   layout="wide")

def user_prompt_submit():
    """
    Callback function that triggers on pressing 'Enter' in the text_input.
    Grabs the typed question, clears it, stores in session state.
    """
    user_input = st.session_state.input
    st.session_state.prompt = user_input
    st.session_state["input"] = ""

if "prompt" not in st.session_state:
    st.session_state.prompt = ""

# Initial greeting from the bot
message("Thank you for your interest in Bakersfield Adult School! What would you like to learn more about?",
        key="-1")

# If the user has submitted a prompt, generate a response
if st.session_state.prompt:
    user_query = st.session_state.prompt
    user_response = generate_response(user_query)
    if user_response.startswith("Error"):
        st.error(user_response)
    else:
        # Display user query
        message(user_query, is_user=True, avatar_style="adventurer", key="user_message")
        # Display bot response
        message(user_response, key="bot_response")

# Text input at bottom
st.text_input(
    key="input",
    on_change=user_prompt_submit,
    label="Type in your question here",
    label_visibility="hidden",
    placeholder="Type in your question here"
)

# Extra styling to pin input at bottom
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
# Optional: Uncomment to test system-prompt demo
#############################################
# generate_workflow_demo()
