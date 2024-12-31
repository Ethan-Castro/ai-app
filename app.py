#############################################
# Imports
#############################################
import streamlit as st
from streamlit_chat import message
import vertexai
from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Tool,
    grounding,
)

#############################################
# Configuration
#############################################

PROJECT_ID = "alisons-apps"  # Replace with your actual project ID
LOCATION = "us-central1"     # Vertex AI location
DATA_STORE_ID = (
    "course_1735593026699"
)

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

#############################################
# Model & Retrieval Setup
#############################################
# Create the retrieval tool referencing your data store.
retrieval = grounding.Retrieval(
    grounding.VertexAISearch(
        datastore=DATA_STORE_ID,
        project=PROJECT_ID,
        location="global",  # As specified by your data store's location
    )
)
retrieval_tool = Tool.from_retrieval(retrieval)

# Instantiate the model you want to use
model = GenerativeModel(model_id="gemini-1.5-flash-001")

#############################################
# Chatbot Helper Function
#############################################
def generate_response(user_input: str) -> str:
    """
    Sends user_input to the GenerativeModel with the retrieval tool.
    Returns the model's textual response.
    """
    try:
        # You can tweak GenerationConfig as needed (temperature, top_p, etc.)
        gen_config = GenerationConfig(
            temperature=0.0,
            max_output_tokens=1024,
        )

        # Provide the user input string + tools for retrieval
        response = model.generate_content(
            prompt=user_input,
            tools=[retrieval_tool],
            generation_config=gen_config,
        )

        # `response.text` contains the final generated text
        return response.text

    except Exception as e:
        return f"Error generating response: {e}"

#############################################
# Streamlit UI
#############################################
st.set_page_config(
    page_title="Vertex AI ChatBot with Retrieval",
    page_icon="🤖",
    layout="wide"
)

def user_prompt_submit():
    """
    Callback function when user presses 'Enter' in the text_input.
    """
    user_input = st.session_state.input
    st.session_state.prompt = user_input
    st.session_state["input"] = ""

if "prompt" not in st.session_state:
    st.session_state.prompt = ""

# Display initial greeting
message("Welcome to the Bakersfield Adult School ChatBot! How can I help you today?", key="initial-bot-message")

if st.session_state.prompt:
    user_query = st.session_state.prompt
    user_response = generate_response(user_query)

    # Show user question
    message(user_query, is_user=True, avatar_style="adventurer", key="user-message")

    # Show response (or error)
    if user_response.startswith("Error"):
        st.error(user_response)
    else:
        message(user_response, key="bot-response")

# Text input pinned at the bottom
st.text_input(
    key="input",
    on_change=user_prompt_submit,
    label="Type your question here",
    label_visibility="hidden",
    placeholder="Ask about schedules, requirements, or anything else..."
)

# CSS styling to keep text input at bottom
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
    #MainMenu {display: none;}
    footer {display: none;}
</style>
"""
st.markdown(styl, unsafe_allow_html=True)
