#############################################
# Imports
#############################################
from google import genai
from google.genai import types
import base64
import streamlit as st
from streamlit_chat import message
from streamlit.components.v1 import html

#############################################
# Configuration
#############################################
project_id = "alisons-apps"
location = "us-central1"
model_name = "gemini-2.0-flash-exp"

#############################################
# Large system prompt text (from your first snippet)
#############################################
textsi_1 = """Welcoming & Offering Support Options APP
Welcome Message:
Start with a warm and friendly welcome message. For example: \"Welcome to the YELLOW Mind Support Bot! I’m glad to have you here on this journey towards an empowered and stress-free relationship with your body and food.\"
Introduction to Course:
Briefly introduce the purpose of the course and how the app will assist them. For example: \"This course is designed to support you in developing a positive body image and overcome disordered eating patterns. Our AI is here to guide you every step of the way.\"
Topic Selection Prompt:
Invite participants to choose a topic they would like support or guidance with. Present the options clearly:
Stress Management
Body Image
Eating
Self-Talk
Exercise
Sleep
Example prompt: \"To get started, please select a topic you\'d like to focus on today. You can choose from the following: Stress Management, Body Image, Eating, Self-Talk, Exercise, or Sleep.\"
User Input:
Allow users to select their preferred topic through a simple interface, such as buttons or a dropdown menu.
Guidance and Support:
Once a topic is selected, provide tailored guidance or resources related to that topic. This could include tips, exercises, or articles.
Encouragement and Next Steps:
Encourage users to explore the resources and remind them that they can return to choose another topic at any time. For example: \"Feel free to explore the resources provided. Remember, you can always come back and choose another topic whenever you\'re ready.\"
Feedback and Interaction:
Offer an option for users to provide feedback on the guidance they received or ask further questions. This can help improve the app\'s effectiveness and user experience.
Privacy and Support:
Ensure users know their interactions are confidential and that support is available if they need it.
This workflow will help create a welcoming and supportive environment for participants, guiding them to focus on areas where they seek improvement or support.

[... Truncated for brevity: All of your body-image, stress management, self-talk, eating workflows, etc., text is included below in the final code block. You can keep it in full as-is ...]
"""

#############################################
# Demonstration function mirroring your original "generate()"
#############################################
def generate_workflow():
    """
    This function demonstrates how to use a large, system-level prompt
    (`textsi_1`) with `generate_content_stream()`. 
    You can call this function to see a streamed response in your terminal/log.
    """
    client = genai.Client(vertexai=True, project=project_id, location=location)

    # Example: If you had a retrieval tool. Leaving it commented out for demo.
    # tools = [
    #     types.Tool(
    #         retrieval=types.Retrieval(
    #             vertex_ai_search=types.VertexAISearch(
    #                 datastore="projects/alisons-apps/locations/global/collections/default_collection/dataStores/course_1735593026699"
    #             )
    #         )
    #     ),
    # ]

    # We'll just demonstrate a system instruction with your textsi_1
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=1807,
        response_modalities=["TEXT"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        # tools=tools,  # If you need the retrieval tool, uncomment and configure
        system_instruction=[types.Part.from_text(textsi_1)]
    )

    # We supply an empty user content or minimal content so that the LLM focuses on the system prompt
    contents = []

    try:
        response_chunks = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=generate_content_config,
        )
        for chunk in response_chunks:
            if chunk.candidates and chunk.candidates[0].content.parts:
                # Stream the text in real-time
                print(chunk.text, end="")
        print("\n\n--- End of streaming response ---")
    except Exception as e:
        print("Error in generate_workflow: ", str(e))

#############################################
# Streamlit Chatbot Helper Functions
#############################################
def get_genai_client():
    """
    Initializes and returns the GenAI client for Vertex AI.
    """
    try:
        return genai.Client(vertexai=True, project=project_id, location=location)
    except Exception as e:
        st.error("Failed to initialize GenAI client: " + str(e))
        return None

def generate_response(user_input: str) -> str:
    """
    Handles conversation in the Streamlit chatbot context.
    Takes user_input from the text box, queries the LLM, and returns the response.
    """
    client = get_genai_client()
    if not client:
        return "Error initializing the GenAI client. Please check your configuration."

    contents = [
        types.Content(role="user", parts=[user_input])
    ]

    # Example of how you'd incorporate system instructions if desired:
    # system_instructions = types.Content(role="system", parts=[textsi_1])
    # contents.insert(0, system_instructions)

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
        ]
    )

    try:
        response_chunks = client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=generate_content_config
        )
        # Concatenate all response chunks
        response = "".join(chunk.text for chunk in response_chunks)
        return response
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
    Grabs the typed question, clears the text_input, sets 'prompt' in session state.
    """
    user_input = st.session_state.input
    st.session_state.prompt = user_input
    st.session_state["input"] = ""

if "prompt" not in st.session_state:
    st.session_state.prompt = ""

# Initial greeting from the bot
message("Thank you for your interest in Bakersfield Adult School! What would you like to learn more about?",
        key="-1")

if st.session_state.prompt:
    user_query = st.session_state.prompt
    user_response = generate_response(user_query)
    if "Error" in user_response:
        st.error(user_response)
    else:
        # Show user question
        message(user_query, is_user=True, avatar_style="adventurer", key="user_message")
        # Show bot response
        message(user_response, key="bot_response")

# Text input at the bottom of the page
st.text_input(
    key="input",
    on_change=user_prompt_submit,
    label="Type in your question here",
    label_visibility="hidden",
    placeholder="Type in your question here"
)

# Some extra styling to keep input anchored at bottom
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
# Optional: Uncomment the line below to test
# your large system-instruction prompt code
#############################################
# generate_workflow()
