import streamlit as st
import vertexai
from vertexai.preview.generative_models import GenerativeModel, SafetySetting, Part, Tool
from vertexai.preview.generative_models import grounding

# Define your generation config and safety settings outside your main function
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

def init_vertex_ai():
    """Initialize Vertex AI with your project and region."""
    vertexai.init(
        project="alisons-apps",
        location="us-central1"
    )

def create_chat():
    """
    Create and return a GenerativeModel chat object with the desired tools.
    This only needs to be done once per session.
    """
    # Define your retrieval-based tool
    tools = [
        Tool.from_retrieval(
            retrieval=grounding.Retrieval(
                source=grounding.VertexAISearch(
                    datastore="projects/alisons-apps/locations/global/collections/default_collection/dataStores/course_1735593026699"
                )
            )
        )
    ]

    # Create the generative model with tools
    model = GenerativeModel(
        model="gemini-1.5-pro-002",
        tools=tools,
    )

    # Start a chat session
    chat = model.start_chat()
    return chat

def main():
    st.title("Multi-turn Chat with Vertex GenerativeModel")

    # Initialize Vertex AI once at the start of the app
    init_vertex_ai()

    # Create a chat session if we haven't already
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = create_chat()

    st.markdown("You can either click the buttons below to run the sample multi-turn queries, "
                "or you can type your own question in the text input.")

    # --- Sample multi-turn queries (as in your original snippet) ---
    col1, col2 = st.columns(2)

    if col1.button("Ask: What is red mind?"):
        response = st.session_state.chat_session.send_message(
            ["What is red mind"],
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        st.write("**Question**: What is red mind?")
        st.write("**Answer**:", response)

    if col2.button("Ask: Who is Alison Ross?"):
        response = st.session_state.chat_session.send_message(
            ["who is alison ross"],
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        st.write("**Question**: Who is Alison Ross?")
        st.write("**Answer**:", response)

    st.write("---")

    # --- Free-form user input ---
    user_query = st.text_input("Or type a custom question here and press 'Send':")

    if st.button("Send"):
        if user_query.strip():
            response = st.session_state.chat_session.send_message(
                [user_query],
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            st.write(f"**Question**: {user_query}")
            st.write("**Answer**:", response)
        else:
            st.warning("Please enter a question first.")

if __name__ == "__main__":
    main()
