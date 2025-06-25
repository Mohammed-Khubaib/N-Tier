# client/main.py
import streamlit as st
import requests
from client.config import config
from client.components.users import render_users_page
from client.components.projects import render_projects_page
from client.components.tasks import render_tasks_page

# Configure Streamlit page
st.set_page_config(
    page_title="Task Management System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_api_connection():
    """Check if the FastAPI server is running"""
    try:
        response = requests.get(f"{config.api_base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def render_dashboard():
    """Render the main dashboard"""
    st.title("📊 Dashboard")
    
    # API Status
    api_status = check_api_connection()
    status_color = "🟢" if api_status else "🔴"
    status_text = "Connected" if api_status else "Disconnected"
    st.markdown(f"**API Status:** {status_color} {status_text}")
    
    if not api_status:
        st.error("⚠️ Cannot connect to the FastAPI server. Please make sure it's running on the configured URL.")
        st.code(f"API URL: {config.api_base_url}")
        return
    
    # Import API client here to avoid import errors if API is down
    from client.api_client import api_client
    
    # Fetch data for dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Quick Stats")
        
        # Get counts
        users = api_client.get_users()
        projects = api_client.get_projects()
        tasks = api_client.get_tasks()
        
        if users is not None and projects is not None and tasks is not None:
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric("👥 Users", len(users))
            
            with col_b:
                st.metric("📁 Projects", len(projects))
            
            with col_c:
                st.metric("📝 Tasks", len(tasks))
            
            # Task completion rate
            if tasks:
                completed_tasks = sum(1 for task in tasks if task.get('is_completed', False))
                completion_rate = (completed_tasks / len(tasks)) * 100
                st.metric("✅ Completion Rate", f"{completion_rate:.1f}%")
        else:
            st.error("Unable to fetch data from API")
    
    with col2:
        st.subheader("🚀 Quick Actions")
        
        if st.button("➕ Create New User", use_container_width=True):
            st.session_state.page = "Users"
            st.rerun()
        
        if st.button("📁 Create New Project", use_container_width=True):
            st.session_state.page = "Projects"
            st.rerun()
        
        if st.button("📝 Create New Task", use_container_width=True):
            st.session_state.page = "Tasks"
            st.rerun()
        
        if st.button("📊 View All Data", use_container_width=True):
            with st.expander("Recent Activity", expanded=True):
                if tasks:
                    recent_tasks = sorted(tasks, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
                    for task in recent_tasks:
                        st.write(f"• **{task['title']}** - {task['status'].replace('_', ' ').title()}")
                else:
                    st.write("No recent activity")

def main():
    """Main application function"""
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    
    # Sidebar navigation
    st.sidebar.title("🎯 Task Management")
    st.sidebar.markdown("---")
    
    # Navigation menu
    pages = {
        "📊 Dashboard": "Dashboard",
        "👥 Users": "Users", 
        "📁 Projects": "Projects",
        "📝 Tasks": "Tasks"
    }
    
    selected_page = st.sidebar.selectbox(
        "Navigate to:",
        options=list(pages.keys()),
        index=list(pages.values()).index(st.session_state.page)
    )
    
    st.session_state.page = pages[selected_page]
    
    # API Configuration in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Configuration")
    st.sidebar.write(f"**API URL:** {config.api_base_url}")
    st.sidebar.write(f"**Timeout:** {config.timeout}s")
    
    # Connection test button
    if st.sidebar.button("🔄 Test Connection"):
        if check_api_connection():
            st.sidebar.success("✅ API Connected")
        else:
            st.sidebar.error("❌ API Disconnected")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💡 Tips:**")
    st.sidebar.markdown("- Make sure FastAPI server is running")
    st.sidebar.markdown("- Check API URL in configuration")
    st.sidebar.markdown("- Use filters to find data quickly")
    
    # Render selected page
    if st.session_state.page == "Dashboard":
        render_dashboard()
    elif st.session_state.page == "Users":
        render_users_page()
    elif st.session_state.page == "Projects":
        render_projects_page()
    elif st.session_state.page == "Tasks":
        render_tasks_page()

if __name__ == "__main__":
    main()