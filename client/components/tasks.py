# client/components/tasks.py
import streamlit as st
import pandas as pd
from datetime import datetime, date
from client.api_client import api_client
from client.utils.helpers import (
    display_success_message, display_error_message, 
    create_data_table, format_datetime, get_status_emoji, 
    get_priority_emoji, confirm_deletion
)

def render_tasks_page():
    """Render the Tasks management page"""
    st.title("📝 Task Management")
    
    # Sidebar for operations
    with st.sidebar:
        st.header("Task Operations")
        operation = st.selectbox(
            "Choose Operation",
            ["View All Tasks", "View Task Details", "Create Task", "Update Task", "Delete Task"]
        )
    
    if operation == "View All Tasks":
        render_tasks_list()
    elif operation == "View Task Details":
        render_task_details()
    elif operation == "Create Task":
        render_create_task()
    elif operation == "Update Task":
        render_update_task()
    elif operation == "Delete Task":
        render_delete_task()

def render_tasks_list():
    """Display all tasks"""
    st.subheader("📋 All Tasks")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_tasks"):
            st.rerun()
    
    tasks = api_client.get_tasks()
    if tasks:
        # Add display formatting
        for task in tasks:
            task['status_display'] = f"{get_status_emoji(task['status'])} {task['status'].replace('_', ' ').title()}"
            task['priority_display'] = f"{get_priority_emoji(task['priority'])} {task['priority'].title()}"
            task['completed_display'] = "✅ Yes" if task['is_completed'] else "⏳ No"
        
        df = create_data_table(tasks, [
            'id', 'title', 'status_display', 'priority_display', 
            'completed_display', 'project_id', 'assignee_id', 'due_date'
        ])
        df.rename(columns={
            'status_display': 'status',
            'priority_display': 'priority',
            'completed_display': 'completed'
        }, inplace=True)
        
        # Display metrics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task['is_completed'])
        pending_tasks = total_tasks - completed_tasks
        
        # Priority breakdown
        priority_counts = {}
        for task in tasks:
            priority = task['priority']
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tasks", total_tasks)
        with col2:
            st.metric("✅ Completed", completed_tasks)
        with col3:
            st.metric("⏳ Pending", pending_tasks)
        with col4:
            st.metric("🔴 Urgent", priority_counts.get('urgent', 0))
        
        # Filters
        with st.expander("🔍 Filters"):
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                status_filter = st.multiselect(
                    "Filter by Status",
                    options=['todo', 'in_progress', 'done'],
                    format_func=lambda x: f"{get_status_emoji(x)} {x.replace('_', ' ').title()}"
                )
            
            with filter_col2:
                priority_filter = st.multiselect(
                    "Filter by Priority",
                    options=['low', 'medium', 'high', 'urgent'],
                    format_func=lambda x: f"{get_priority_emoji(x)} {x.title()}"
                )
            
            with filter_col3:
                completion_filter = st.selectbox(
                    "Filter by Completion",
                    options=['All', 'Completed', 'Pending']
                )
        
        # Apply filters
        filtered_tasks = tasks.copy()
        if status_filter:
            filtered_tasks = [task for task in filtered_tasks if task['status'] in status_filter]
        if priority_filter:
            filtered_tasks = [task for task in filtered_tasks if task['priority'] in priority_filter]
        if completion_filter == 'Completed':
            filtered_tasks = [task for task in filtered_tasks if task['is_completed']]
        elif completion_filter == 'Pending':
            filtered_tasks = [task for task in filtered_tasks if not task['is_completed']]
        
        # Update display with filtered data
        if filtered_tasks != tasks:
            st.info(f"Showing {len(filtered_tasks)} of {total_tasks} tasks")
            for task in filtered_tasks:
                task['status_display'] = f"{get_status_emoji(task['status'])} {task['status'].replace('_', ' ').title()}"
                task['priority_display'] = f"{get_priority_emoji(task['priority'])} {task['priority'].title()}"
                task['completed_display'] = "✅ Yes" if task['is_completed'] else "⏳ No"
            
            df = create_data_table(filtered_tasks, [
                'id', 'title', 'status_display', 'priority_display', 
                'completed_display', 'project_id', 'assignee_id', 'due_date'
            ])
            df.rename(columns={
                'status_display': 'status',
                'priority_display': 'priority',
                'completed_display': 'completed'
            }, inplace=True)
        
        # Display table
        st.dataframe(df, use_container_width=True)
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"tasks_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No tasks found or unable to fetch tasks.")

def render_task_details():
    """Display detailed view of a specific task"""
    st.subheader("🔍 Task Details")
    
    tasks = api_client.get_tasks()
    if not tasks:
        st.error("Unable to fetch tasks")
        return
    
    task_options = {f"{task['title']} ({task['id']})": task['id'] for task in tasks}
    selected_task = st.selectbox("Select Task", list(task_options.keys()))
    
    if selected_task:
        task_id = task_options[selected_task]
        task = api_client.get_task(task_id)
        
        if task:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Task Information**")
                st.write(f"**ID:** {task['id']}")
                st.write(f"**Title:** {task['title']}")
                st.write(f"**Status:** {get_status_emoji(task['status'])} {task['status'].replace('_', ' ').title()}")
                st.write(f"**Priority:** {get_priority_emoji(task['priority'])} {task['priority'].title()}")
                st.write(f"**Completed:** {'✅ Yes' if task['is_completed'] else '⏳ No'}")
                st.write(f"**Project ID:** {task['project_id']}")
                st.write(f"**Assignee ID:** {task['assignee_id'] if task['assignee_id'] else 'Not assigned'}")
            
            with col2:
                st.write("**Timestamps**")
                st.write(f"**Created:** {format_datetime(task['created_at'])}")
                st.write(f"**Updated:** {format_datetime(task.get('updated_at'))}")
                st.write(f"**Due Date:** {format_datetime(task.get('due_date'))}")
            
            if task.get('description'):
                st.write("**Description**")
                st.write(task['description'])

def render_create_task():
    """Create new task form"""
    st.subheader("➕ Create New Task")
    
    # Get projects and users for selection
    projects = api_client.get_projects()
    users = api_client.get_users()
    
    if not projects:
        st.error("Unable to fetch projects. Please create projects first.")
        return
    
    project_options = {f"{project['name']} ({project['id']})": project['id'] for project in projects}
    user_options = {f"{user['full_name']} ({user['username']})": user['id'] for user in users} if users else {}
    
    with st.form("create_task_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Task Title *", placeholder="Enter task title")
            project = st.selectbox("Project *", list(project_options.keys()))
            status = st.selectbox(
                "Status",
                ["todo", "in_progress", "done"],
                format_func=lambda x: f"{get_status_emoji(x)} {x.replace('_', ' ').title()}"
            )
        
        with col2:
            priority = st.selectbox(
                "Priority",
                ["low", "medium", "high", "urgent"],
                index=1,  # default to medium
                format_func=lambda x: f"{get_priority_emoji(x)} {x.title()}"
            )
            
            assignee = st.selectbox(
                "Assignee (Optional)",
                ["None"] + list(user_options.keys()) if user_options else ["None"]
            )
            
            due_date = st.date_input("Due Date (Optional)", value=None)
        
        description = st.text_area("Description", placeholder="Enter task description (optional)")
        
        submitted = st.form_submit_button("Create Task", type="primary")
        
        if submitted:
            if not all([title, project]):
                st.error("Please fill in all required fields marked with *")
            else:
                task_data = {
                    "title": title,
                    "description": description if description else None,
                    "priority": priority,
                    "project_id": project_options[project],
                    "assignee_id": user_options[assignee] if assignee != "None" and assignee in user_options else None,
                    "due_date": due_date.isoformat() if due_date else None
                }
                
                result = api_client.create_task(task_data)
                if result:
                    display_success_message(f"Task '{title}' created successfully!")
                    st.rerun()

def render_update_task():
    """Update existing task form"""
    st.subheader("✏️ Update Task")
    
    tasks = api_client.get_tasks()
    if not tasks:
        st.error("Unable to fetch tasks")
        return
    
    task_options = {f"{task['title']} ({task['id']})": task['id'] for task in tasks}
    selected_task = st.selectbox("Select Task to Update", list(task_options.keys()))
    
    if selected_task:
        task_id = task_options[selected_task]
        task = api_client.get_task(task_id)
        
        if task:
            # Get users for assignee selection
            users = api_client.get_users()
            user_options = {f"{user['full_name']} ({user['username']})": user['id'] for user in users} if users else {}
            
            # Find current assignee
            current_assignee = "None"
            if task['assignee_id'] and users:
                for user in users:
                    if user['id'] == task['assignee_id']:
                        current_assignee = f"{user['full_name']} ({user['username']})"
                        break
            
            with st.form("update_task_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    title = st.text_input("Task Title", value=task['title'])
                    status = st.selectbox(
                        "Status",
                        ["todo", "in_progress", "done"],
                        index=["todo", "in_progress", "done"].index(task['status']),
                        format_func=lambda x: f"{get_status_emoji(x)} {x.replace('_', ' ').title()}"
                    )
                    is_completed = st.checkbox("Mark as Completed", value=task['is_completed'])
                
                with col2:
                    priority = st.selectbox(
                        "Priority",
                        ["low", "medium", "high", "urgent"],
                        index=["low", "medium", "high", "urgent"].index(task['priority']),
                        format_func=lambda x: f"{get_priority_emoji(x)} {x.title()}"
                    )
                    
                    assignee_options = ["None"] + list(user_options.keys()) if user_options else ["None"]
                    assignee_index = 0
                    if current_assignee in assignee_options:
                        assignee_index = assignee_options.index(current_assignee)
                    
                    assignee = st.selectbox(
                        "Assignee",
                        assignee_options,
                        index=assignee_index
                    )
                    
                    # Parse current due date
                    current_due_date = None
                    if task.get('due_date'):
                        try:
                            current_due_date = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00')).date()
                        except:
                            pass
                    
                    due_date = st.date_input("Due Date", value=current_due_date)
                
                description = st.text_area("Description", value=task.get('description', ''))
                
                submitted = st.form_submit_button("Update Task", type="primary")
                
                if submitted:
                    update_data = {}
                    if title != task['title']:
                        update_data['title'] = title
                    if status != task['status']:
                        update_data['status'] = status
                    if priority != task['priority']:
                        update_data['priority'] = priority
                    if is_completed != task['is_completed']:
                        update_data['is_completed'] = is_completed
                    if description != task.get('description', ''):
                        update_data['description'] = description
                    
                    # Handle assignee update
                    new_assignee_id = user_options[assignee] if assignee != "None" and assignee in user_options else None
                    if new_assignee_id != task['assignee_id']:
                        update_data['assignee_id'] = new_assignee_id
                    
                    # Handle due date update
                    new_due_date = due_date.isoformat() if due_date else None
                    current_due_date_str = task.get('due_date')
                    if current_due_date_str:
                        try:
                            current_due_date_str = datetime.fromisoformat(current_due_date_str.replace('Z', '+00:00')).date().isoformat()
                        except:
                            current_due_date_str = None
                    
                    if new_due_date != current_due_date_str:
                        update_data['due_date'] = new_due_date
                    
                    if update_data:
                        result = api_client.update_task(task_id, update_data)
                        if result:
                            display_success_message(f"Task '{title}' updated successfully!")
                            st.rerun()
                    else:
                        st.info("No changes detected.")

def render_delete_task():
    """Delete task form"""
    st.subheader("🗑️ Delete Task")
    
    tasks = api_client.get_tasks()
    if not tasks:
        st.error("Unable to fetch tasks")
        return
    
    task_options = {f"{task['title']} ({task['id']})": task['id'] for task in tasks}
    selected_task = st.selectbox("Select Task to Delete", list(task_options.keys()))
    
    if selected_task:
        task_id = task_options[selected_task]
        task = api_client.get_task(task_id)
        
        if task:
            st.warning("⚠️ **Warning:** This action cannot be undone!")
            st.write(f"**Task to delete:** {task['title']}")
            st.write(f"**Status:** {get_status_emoji(task['status'])} {task['status'].replace('_', ' ').title()}")
            st.write(f"**Priority:** {get_priority_emoji(task['priority'])} {task['priority'].title()}")
            
            if confirm_deletion("task", task['title']):
                if st.button("🗑️ Delete Task", type="primary"):
                    result = api_client.delete_task(task_id)
                    if result:
                        display_success_message(f"Task '{task['title']}' deleted successfully!")
                        st.rerun()