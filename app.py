import streamlit as st

# Sidebar: Active Project and Old Projects
st.sidebar.title("Agentic Assignment Evaluator")

# Initialize session state for active project
if "active_project" not in st.session_state:
    st.session_state["active_project"] = "Untitled Project"

# Display active project name
st.sidebar.write(f"**Active Project:** {st.session_state['active_project']}")

# Expander to display old projects
with st.sidebar.expander("Old Projects", expanded=False):
    st.write("Here are your saved projects:")
    # Placeholder for dynamically loaded projects
    # Replace the list below with your actual project fetching logic
    projects = ["Project 1", "Project 2", "Project 3"]
    for project in projects:
        if st.button(f"Open {project}"):
            st.session_state["active_project"] = project
            st.experimental_rerun()  # Reload the app to reflect the new active project

# Sidebar Menu (Updated)
menu = st.sidebar.radio("Navigation", ["Upload Brief", "Submit Assignment"])

# Main Content
if menu == "Upload Brief":
    st.title("Upload Assignment Brief")
    st.write(
        "In this section, you can upload your assignment brief. "
        "Make sure it's in PDF format. We'll analyze it and provide guidelines."
    )
    project_name = st.text_input("Enter a name for this project:", st.session_state["active_project"])
    st.session_state["active_project"] = project_name  # Update the project name dynamically
    uploaded_file = st.file_uploader("Upload your assignment brief (PDF)", type=["pdf"])
    if uploaded_file:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        # Placeholder for processing logic
        st.text("Processing your brief...")

elif menu == "Submit Assignment":
    st.title("Submit Assignment")
    st.write(
        "Upload your completed assignment in this section. "
        "We'll evaluate it based on the brief and provide comments and a projected score."
    )
    uploaded_assignment = st.file_uploader("Upload your completed assignment (PDF)", type=["pdf"])
    if uploaded_assignment:
        st.success(f"Assignment '{uploaded_assignment.name}' uploaded successfully!")
        # Placeholder for evaluation logic
        st.text("Evaluating your assignment...")
