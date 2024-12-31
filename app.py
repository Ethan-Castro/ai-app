########################################
# 1) Imports and Dependencies
########################################

# Streamlit is the Python library used for creating this UI.
import streamlit as st

# The Google GENAI client and associated types for making
# requests to Vertex AI (Gemini model) and specifying tools/config.
from google import genai
from google.genai import types

# base64 is not strictly necessary here, but it's included
# because your original code imported it. It's often used
# for encoding/decoding data (e.g., images or credentials).
import base64


########################################
# 2) Page Configuration
########################################

# This sets up some of the basic look-and-feel properties
# of your Streamlit app: the page title, icon, layout, etc.
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon=":robot_face:",
    layout="centered",
    initial_sidebar_state="collapsed",
)


########################################
# 3) Title and Description
########################################

# Display a title at the top of the page.
st.title("Gemini Chatbot Demo")

# Display a short description of how to use the app.
st.write("Enter your question/prompt below to interact with the Gemini model in real-time.")


########################################
# 4) Session State for Conversation
########################################

# We'll store the conversation in the session state so that
# the conversation does not get reset on each interaction.
if "generated_responses" not in st.session_state:
    st.session_state.generated_responses = []

if "user_queries" not in st.session_state:
    st.session_state.user_queries = []


########################################
# 5) Chat Input
########################################

# Create a user input box using Streamlit's chat_input (newer
# Streamlit feature). If not available, you can use st.text_input.
user_input = st.chat_input("Ask the Gemini model anything...")

# Alternatively, if you don't have the chat_input widget (older Streamlit versions),
# you can use the following:
# user_input = st.text_input("Ask the Gemini model anything...")


########################################
# 6) Define the Generate Function
########################################

def generate_response(prompt: str) -> str:
    """
    Generates a response by calling the Google Vertex AI
    (Gemini-2.0-flash-exp) model via the google.genai client.

    Returns the full response text from the streaming output.
    """

    # 6.1) Initialize the GENAI Client
    # Note: This assumes that you have set up authentication
    # with GOOGLE_APPLICATION_CREDENTIALS or are running in
    # an environment that has the necessary GCP credentials.
    client = genai.Client(
        vertexai=True,            # Tells the client we're using Vertex AI
        project="alisons-apps",   # Your GCP project ID
        location="us-central1"    # Region for the model
    )

    # 6.2) Define the model name you want to use
    model_name = "gemini-2.0-flash-exp"

    # 6.3) Create the input to the model. In your original snippet,
    # the contents list was empty. Here, we populate it with the
    # user’s prompt so the model can respond.
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(text=prompt)
            ]
        )
    ]

    # 6.4) Define any tools you want to configure. In your snippet,
    # you included a retrieval tool pointing to a Vertex AI Search
    # datastore. This allows the model to retrieve additional context
    # from the specified dataStore.
    tools = [
        types.Tool(
            retrieval=types.Retrieval(
                vertex_ai_search=types.VertexAISearch(
                    datastore="projects/alisons-apps/locations/global/collections/default_collection/dataStores/course_1735593026699"
                )
            )
        ),
    ]

    # 6.5) GenerateContentConfig contains parameters that influence
    # how the model responds (temperature, top_p, max tokens, etc.),
    # as well as the safety settings and which tools are passed in.
    generate_content_config = types.GenerateContentConfig(
        temperature=1,               # Higher temperature -> more "creative" output
        top_p=0.95,
        max_output_tokens=1807,
        response_modalities=["TEXT"],
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="OFF"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="OFF"
            )
        ],
        tools=tools,
    )

    # 6.6) We will use generate_content_stream to stream the results
    # from the model. This returns chunks of content, which we can
    # process incrementally.
    # We'll concatenate the streamed text parts into a single string.
    streamed_response = ""

    # Execute the streaming content generation request.
    for chunk in client.models.generate_content_stream(
        model=model_name,
        contents=contents,
        config=generate_content_config
    ):
        # Check if we have a valid chunk of text
        if not chunk.candidates or not chunk.candidates[0].content.parts:
            continue

        # Append the chunk's text to our streaming_response
        streamed_response += chunk.text

    return streamed_response


########################################
# 7) Handle User Input
########################################

# If the user types something into the input box...
if user_input:
    # Save user prompt in session state for display
    st.session_state.user_queries.append(user_input)

    # Generate a response
    output = generate_response(user_input)

    # Save model response in session state for display
    st.session_state.generated_responses.append(output)


########################################
# 8) Display the Conversation
########################################

# Use the chat_message feature to show the conversation in a chat-like interface.
# (Available in newer versions of Streamlit)
if st.session_state.user_queries:
    for i, query in enumerate(st.session_state.user_queries):
        user_msg = query
        bot_msg = st.session_state.generated_responses[i]

        # Display the user's message
        with st.chat_message("user"):
            st.markdown(user_msg)

        # Display the bot's response
        with st.chat_message("assistant"):
            st.markdown(bot_msg)
