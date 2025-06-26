import streamlit as st
import pandas as pd
from client.api_client import api_client
from client.utils.helpers import (
    display_success_message, display_error_message, 
    create_data_table, format_datetime, get_status_emoji, confirm_deletion
)

def render_projects_page():
    """Render the Projects management page"""
    st.title("📁 Project Management")
    
    # Sidebar for operations
    with st.sidebar:
        st.header("Project Operations")
        operation = st.selectbox(
            "Choose Operation",
            ["Create Project", "Update Project", "Delete Project", "View All Projects", "View Project Details"]
        )
    
    if operation == "View All Projects":
        render_projects_list()
    elif operation == "View Project Details":
        render_project_details()
    elif operation == "Create Project":
        render_create_project()
    elif operation == "Update Project":
        render_update_project()
    elif operation == "Delete Project":
        render_delete_project()

def render_projects_list():
    """Display all projects"""
    st.subheader("📋 All Projects")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_projects"):
            st.rerun()
    
    projects = api_client.get_projects()
    if projects:
        # Add status emojis
        for project in projects:
            project['status_display'] = f"{get_status_emoji(project['status'])} {project['status'].replace('_', ' ').title()}"
        
        df = create_data_table(projects, ['id', 'name', 'status_display', 'owner_id', 'created_at'])
        df.rename(columns={'status_display': 'status'}, inplace=True)
        
        # Display metrics
        total_projects = len(projects)
        status_counts = {}
        for project in projects:
            status = project['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        cols = st.columns(len(status_counts) + 1)
        with cols[0]:
            st.metric("Total Projects", total_projects)
        
        for i, (status, count) in enumerate(status_counts.items(), 1):
            with cols[i]:
                st.metric(f"{get_status_emoji(status)} {status.replace('_', ' ').title()}", count)
        
        # Display table
        st.dataframe(df, use_container_width=True)
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"projects_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No projects found or unable to fetch projects.")

def render_project_details():
    """Display detailed view of a specific project"""
    st.subheader("🔍 Project Details")
    
    projects = api_client.get_projects()
    if not projects:
        st.error("Unable to fetch projects")
        return
    
    project_options = {f"{project['name']} ({project['id']})": project['id'] for project in projects}
    selected_project = st.selectbox("Select Project", list(project_options.keys()))
    
    if selected_project:
        project_id = project_options[selected_project]
        project = api_client.get_project(project_id)
        
        if project:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Project Information**")
                st.write(f"**ID:** {project['id']}")
                st.write(f"**Name:** {project['name']}")
                st.write(f"**Status:** {get_status_emoji(project['status'])} {project['status'].replace('_', ' ').title()}")
                st.write(f"**Owner ID:** {project['owner_id']}")
            
            with col2:
                st.write("**Timestamps**")
                st.write(f"**Created:** {format_datetime(project['created_at'])}")
                st.write(f"**Updated:** {format_datetime(project.get('updated_at'))}")
            
            if project.get('description'):
                st.write("**Description**")
                st.write(project['description'])

def render_create_project():
    """Create new project form"""
    st.subheader("➕ Create New Project")
    
    # Get users for owner selection
    users = api_client.get_users()
    if not users:
        st.error("Unable to fetch users. Please create users first.")
        return
    
    user_options = {f"{user['full_name']} ({user['username']})": user['id'] for user in users}
    
    with st.form("create_project_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Project Name *", placeholder="Enter project name")
            owner = st.selectbox("Project Owner *", list(user_options.keys()))
        
        with col2:
            status = st.selectbox(
                "Status",
                ["planning", "in_progress", "completed", "on_hold"],
                format_func=lambda x: f"{get_status_emoji(x)} {x.replace('_', ' ').title()}"
            )
        
        description = st.text_area("Description", placeholder="Enter project description (optional)")
        
        submitted = st.form_submit_button("Create Project", type="primary")
        
        if submitted:
            if not all([name, owner]):
                st.error("Please fill in all required fields marked with *")
            else:
                project_data = {
                    "name": name,
                    "description": description if description else None,
                    "owner_id": user_options[owner]
                }
                
                result = api_client.create_project(project_data)
                if result:
                    display_success_message(f"Project '{name}' created successfully!")
                    st.rerun()

def render_update_project():
    """Update existing project form"""
    st.subheader("✏️ Update Project")
    
    projects = api_client.get_projects()
    if not projects:
        st.error("Unable to fetch projects")
        return
    
    project_options = {f"{project['name']} ({project['id']})": project['id'] for project in projects}
    selected_project = st.selectbox("Select Project to Update", list(project_options.keys()))
    
    if selected_project:
        project_id = project_options[selected_project]
        project = api_client.get_project(project_id)
        
        if project:
            with st.form("update_project_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Project Name", value=project['name'])
                    status = st.selectbox(
                        "Status",
                        ["planning", "in_progress", "completed", "on_hold"],
                        index=["planning", "in_progress", "completed", "on_hold"].index(project['status']),
                        format_func=lambda x: f"{get_status_emoji(x)} {x.replace('_', ' ').title()}"
                    )
                
                description = st.text_area("Description", value=project.get('description', ''))
                
                submitted = st.form_submit_button("Update Project", type="primary")
                
                if submitted:
                    update_data = {}
                    if name != project['name']:
                        update_data['name'] = name
                    if status != project['status']:
                        update_data['status'] = status
                    if description != project.get('description', ''):
                        update_data['description'] = description
                    
                    if update_data:
                        result = api_client.update_project(project_id, update_data)
                        if result:
                            display_success_message(f"Project '{name}' updated successfully!")
                            st.rerun()
                    else:
                        st.info("No changes detected.")

def render_delete_project():
    """Delete project form"""
    st.subheader("🗑️ Delete Project")
    
    projects = api_client.get_projects()
    if not projects:
        st.error("Unable to fetch projects")
        return
    
    project_options = {f"{project['name']} ({project['id']})": project['id'] for project in projects}
    selected_project = st.selectbox("Select Project to Delete", list(project_options.keys()))
    
    if selected_project:
        project_id = project_options[selected_project]
        project = api_client.get_project(project_id)
        
        if project:
            st.warning("⚠️ **Warning:** This action will also delete all tasks associated with this project!")
            st.write(f"**Project to delete:** {project['name']}")
            st.write(f"**Status:** {get_status_emoji(project['status'])} {project['status'].replace('_', ' ').title()}")
            
            if confirm_deletion("project", project['name']):
                if st.button("🗑️ Delete Project", type="primary"):
                    result = api_client.delete_project(project_id)
                    if result:
                        display_success_message(f"Project '{project['name']}' deleted successfully!")
                        st.rerun()