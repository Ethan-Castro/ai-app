import google.generativeai as genai
from google.generativeai import types
import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Course Chatbot",
    page_icon=":robot_face:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Initialize Session State for Messages ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Initialize Vertex AI Client (outside the message loop for efficiency) ---
try:
    client = genai.Client(
        vertexai=True,
        project="alisons-apps",
        location="us-central1"
    )
except Exception as e:
    st.error(f"Error initializing Vertex AI Client: {e}")
    st.stop()

model_name = "gemini-2.0-flash-exp"
tools_config = [
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
    tools=tools_config,
)

# --- Chatbot Interface ---
st.title("Course Chatbot")
st.write("Ask me anything about the course content!")

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

    # Prepare content for the model
    contents = [
      types.Content(
          role="user",
          parts=[
              types.Part(text=prompt)
          ]
      )
    ]

    # Generate the response from the model
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=generate_content_config
        )

        if response.candidates and response.candidates[0].content.parts:
            bot_response = response.candidates[0].content.parts[0].text
        else:
            bot_response = "Sorry, I couldn't generate a response at this time."

    except Exception as e:
        bot_response = f"An error occurred while generating the response: {e}"
        st.error(bot_response)

    # Display assistant response and add it to the state
    with st.chat_message("assistant"):
        st.markdown(bot_response)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

# --- Instructions for Running ---
st.markdown("""
---
**How to run this app:**
1. **Save:** Save this code as a Python file (e.g., `chatbot_app.py`).
2. **Install Libraries:** Make sure you have the required libraries installed:
    ```bash
    pip install streamlit google-generativeai
    ```
3. **Run:** Open your terminal, navigate to the directory where you saved the file, and run:
    ```bash
    streamlit run chatbot_app.py
    ```

**Important Notes:**
*   **Vertex AI Setup:** This code assumes you have correctly set up your Vertex AI project, have the necessary permissions, and have a data store configured as specified in the `tools_config`.
*   **API Key/Credentials:** The `genai.Client` automatically handles authentication using your Google Cloud credentials (e.g., through `gcloud auth login` or environment variables).
*   **Error Handling:** Basic error handling is included, but you might want to add more robust error checks for production environments.
*   **Customization:** You can customize the chatbot's behavior by adjusting the parameters in `generate_content_config` (e.g., temperature, safety settings).
""")
Use code with caution.
