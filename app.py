from google import genai
from google.genai import types
import base64
import streamlit as st

st.title("Course Chatbot")
st.write("Ask me anything about the course content!")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("What is your question?"):
    # Add user message to the state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Initialize the GenerativeModel inside the interaction
    client = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        client=genai.Client(
            vertexai=True,
            project="alisons-apps",
            location="us-central1"
        )
    )

    # Configure the content and tools for the model
    contents = [
        {"role": "user", "parts": [prompt]}
    ]
    tools = [
        types.Tool(retrieval=types.Retrieval(vertex_ai_search=types.VertexAISearch(datastore="projects/alisons-apps/locations/global/collections/default_collection/dataStores/course_1735593026699"))),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=1807,
        response_modalities=["TEXT"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
        ],
        tools=tools,
    )

    # Generate the response from the model
    response = client.generate_content(
        contents=contents,
        generation_config=generate_content_config
    )

    # Display assistant response and add it to the state
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
