import streamlit as st
import pandas as pd
from client.api_client import api_client

from client.utils.helpers import (
    display_success_message, display_error_message, 
    create_data_table, format_datetime, confirm_deletion
)

def render_users_page():
    """Render the Users management page"""
    st.title("👥 User Management")
    
    # Sidebar for operations
    with st.sidebar:
        st.header("User Operations")
        operation = st.selectbox(
            "Choose Operation",
            ["View All Users", "View User Details", "Create User", "Update User", "Delete User"]
        )
    
    if operation == "View All Users":
        render_users_list()
    elif operation == "View User Details":
        render_user_details()
    elif operation == "Create User":
        render_create_user()
    elif operation == "Update User":
        render_update_user()
    elif operation == "Delete User":
        render_delete_user()

def render_users_list():
    """Display all users"""
    st.subheader("📋 All Users")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_users"):
            st.rerun()
    
    users = api_client.get_users()
    if users:
        df = create_data_table(users, ['id', 'username', 'email', 'full_name', 'is_active', 'created_at'])
        
        # Display metrics
        total_users = len(users)
        active_users = sum(1 for user in users if user.get('is_active', True))
        inactive_users = total_users - active_users
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Active Users", active_users)
        with col3:
            st.metric("Inactive Users", inactive_users)
        
        # Display table
        st.dataframe(df, use_container_width=True)
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"users_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No users found or unable to fetch users.")

def render_user_details():
    """Display detailed view of a specific user"""
    st.subheader("🔍 User Details")
    
    users = api_client.get_users()
    if not users:
        st.error("Unable to fetch users")
        return
    
    user_options = {f"{user['username']} ({user['id']})": user['id'] for user in users}
    selected_user = st.selectbox("Select User", list(user_options.keys()))
    
    if selected_user:
        user_id = user_options[selected_user]
        user = api_client.get_user(user_id)
        
        if user:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Basic Information**")
                st.write(f"**ID:** {user['id']}")
                st.write(f"**Username:** {user['username']}")
                st.write(f"**Email:** {user['email']}")
                st.write(f"**Full Name:** {user['full_name']}")
                st.write(f"**Status:** {'🟢 Active' if user['is_active'] else '🔴 Inactive'}")
            
            with col2:
                st.write("**Timestamps**")
                st.write(f"**Created:** {format_datetime(user['created_at'])}")
                st.write(f"**Updated:** {format_datetime(user.get('updated_at'))}")

def render_create_user():
    """Create new user form"""
    st.subheader("➕ Create New User")
    
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username *", placeholder="Enter username")
            email = st.text_input("Email *", placeholder="user@example.com")
        
        with col2:
            full_name = st.text_input("Full Name *", placeholder="Enter full name")
            is_active = st.checkbox("Active User", value=True)
        
        submitted = st.form_submit_button("Create User", type="primary")
        
        if submitted:
            if not all([username, email, full_name]):
                st.error("Please fill in all required fields marked with *")
            else:
                user_data = {
                    "username": username,
                    "email": email,
                    "full_name": full_name
                }
                
                result = api_client.create_user(user_data)
                if result:
                    display_success_message(f"User '{username}' created successfully!")
                    st.rerun()

def render_update_user():
    """Update existing user form"""
    st.subheader("✏️ Update User")
    
    users = api_client.get_users()
    if not users:
        st.error("Unable to fetch users")
        return
    
    user_options = {f"{user['username']} ({user['id']})": user['id'] for user in users}
    selected_user = st.selectbox("Select User to Update", list(user_options.keys()))
    
    if selected_user:
        user_id = user_options[selected_user]
        user = api_client.get_user(user_id)
        
        if user:
            with st.form("update_user_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    username = st.text_input("Username", value=user['username'])
                    email = st.text_input("Email", value=user['email'])
                
                with col2:
                    full_name = st.text_input("Full Name", value=user['full_name'])
                    is_active = st.checkbox("Active User", value=user['is_active'])
                
                submitted = st.form_submit_button("Update User", type="primary")
                
                if submitted:
                    update_data = {}
                    if username != user['username']:
                        update_data['username'] = username
                    if email != user['email']:
                        update_data['email'] = email
                    if full_name != user['full_name']:
                        update_data['full_name'] = full_name
                    if is_active != user['is_active']:
                        update_data['is_active'] = is_active
                    
                    if update_data:
                        result = api_client.update_user(user_id, update_data)
                        if result:
                            display_success_message(f"User '{username}' updated successfully!")
                            st.rerun()
                    else:
                        st.info("No changes detected.")

def render_delete_user():
    """Delete user form"""
    st.subheader("🗑️ Delete User")
    
    users = api_client.get_users()
    if not users:
        st.error("Unable to fetch users")
        return
    
    user_options = {f"{user['username']} ({user['id']})": user['id'] for user in users}
    selected_user = st.selectbox("Select User to Delete", list(user_options.keys()))
    
    if selected_user:
        user_id = user_options[selected_user]
        user = api_client.get_user(user_id)
        
        if user:
            st.warning("⚠️ **Warning:** This action cannot be undone!")
            st.write(f"**User to delete:** {user['full_name']} ({user['username']})")
            
            if confirm_deletion("user", user['username']):
                if st.button("🗑️ Delete User", type="primary"):
                    result = api_client.delete_user(user_id)
                    if result:
                        display_success_message(f"User '{user['username']}' deleted successfully!")
                        st.rerun()