import streamlit as st
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv
import json

load_dotenv()  # Load variables from .env file

# Configure Gemini API Key (Use environment variables for security)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("Please set the GEMINI_API_KEY environment variable.")
    st.stop()
genai.configure(api_key=GEMINI_API_KEY)


def save_project(project_name, conversation_history):
    """Saves the project and its conversation history to a JSON file."""
    project_data = {"name": project_name, "history": conversation_history}
    try:
        with open(f"{project_name}.json", "w") as f:
            json.dump(project_data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving project: {e}")

# ... (rest of the code)

# Load Projects (Optional)
def load_projects():
    import glob
    projects = {}
    for filename in glob.glob("*.json"):
        try:
            with open(filename, 'r') as f:
                project_data = json.load(f)
                projects[project_data['name']] = project_data['history']
        except Exception as e:
            st.error(f"Error loading project: {e}")
    return projects

# In the sidebar's "Old Projects" expander:
with st.sidebar.expander("Old Projects", expanded=False):
    projects = load_projects()
    if projects:
        for project_name, history in projects.items():
            if st.button(f"Open {project_name}"):
                st.session_state["active_project"] = project_name
                st.session_state["conversation_history"] = history
                st.experimental_rerun()
    else:
        st.write("No saved projects yet.")
def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    try:
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file
    except Exception as e:
        st.error(f"Error uploading file to Gemini: {e}")
        return None

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    if not files:
        return
    st.info("Waiting for file processing...")
    my_bar = st.progress(0)
    for i, name in enumerate((file.name for file in files)):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            time.sleep(5)  # Reduce sleep time for faster feedback
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
        my_bar.progress((i + 1) / len(files))
    st.success("File processing complete.")

def create_generation_config():
    """Creates the configuration for text generation."""
    return {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

def get_model(model_name="gemini-2.0-flash-exp"):
    """Creates the generative model with instructions."""
    generation_config = create_generation_config()
    system_instruction = (
        "You are a student assignment helper and your job is to understand"
        " the uploaded assignment brief, analyze it, check details like deliverables,"
        " grading scheme, assignment requirements and any special instructions and"
        " finally prepare a road map (step by step guideline) for the students"
        " which they can follow to complete the assignment."
    )
    return genai.GenerativeModel(
        model_name=model_name, generation_config=generation_config, system_instruction=system_instruction
    )

# Streamlit App
st.sidebar.title("Agentic Assignment Evaluator")

# Initialize session state for active project and conversation history
if "active_project" not in st.session_state:
    st.session_state["active_project"] = "Untitled Project"
    st.session_state["conversation_history"] = []

# Display active project name
st.sidebar.write(f"**Active Project:** {st.session_state['active_project']}")

# Expander to display old projects (Placeholder)
with st.sidebar.expander("Old Projects", expanded=False):
    st.write("No saved projects yet.")

# Sidebar Menu
menu = st.sidebar.radio("Navigation", ["Upload Brief", "Submit Assignment"])

# Main content
if menu == "Upload Brief":
    st.title("Upload Assignment Brief")
    st.write(
        "Upload your assignment brief (PDF). We'll analyze it and provide guidelines."
    )
    project_name = st.text_input("Enter a name for this project:", st.session_state["active_project"])
    st.session_state["active_project"] = project_name

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")

        # Save the uploaded file temporarily
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Analyzing the brief..."):
            uploaded_file_gemini = upload_to_gemini(uploaded_file.name, mime_type="application/pdf")
            wait_for_files_active([uploaded_file_gemini])

            if uploaded_file_gemini:  # Check if upload was successful
                model = get_model()

                chat_session = model.start_chat(history=st.session_state["conversation_history"])

                user_query = "Generate step by step guide for the completion of this assignment"
                response = chat_session.send_message(user_query)
                st.write(response.text)

                st.session_state["conversation_history"].append({"role": "user", "parts": [user_query]})
                st.session_state["conversation_history"].append({"role": "model", "parts": [response.text]})

                col1, col2 = st.columns(2)
                if col1.button("Step Completed"):
                    save_project(st.session_state["active_project"], st.session_state["conversation_history"])
                    st.success(f"Project '{st.session_state['active_project']}' saved!")
                if col2.button("Need more on brief"):
                    additional_query = st.text_input("Enter your query:")
                    if additional_query:
                        response = chat_session.send_message(additional_query)
                        st.write(response.text)
                        st.session_state["conversation_history"].append({"role": "user", "parts": [additional_query]})
                        st.session_state["conversation_history"].append({"role": "model", "parts": [response.text]})

        # Remove temporary file after processing
        os.remove(uploaded_file.name)

elif menu == "Submit Assignment":
    st.title("Submit Assignment")
    st.write("Upload your completed assignment for evaluation.")
    uploaded_assignment = st.file_uploader("Upload Assignment (PDF)", type=["pdf"])
    if uploaded_assignment:
        st.success(f"Assignment '{uploaded_assignment.name}' uploaded successfully!")
        st.text("Evaluation is not implemented yet.")

# (Optional) Implement functionality for loading projects from saved JSON files