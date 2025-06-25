import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any

def display_success_message(message: str):
    """Display success message"""
    st.success(f"✅ {message}")

def display_error_message(message: str):
    """Display error message"""
    st.error(f"❌ {message}")

def format_datetime(dt_str: Optional[str]) -> str:
    """Format datetime string for display"""
    if not dt_str:
        return "Not set"
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_str

def create_data_table(data: List[Dict], columns: List[str]) -> pd.DataFrame:
    """Create pandas DataFrame for display"""
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    
    # Format datetime columns
    for col in df.columns:
        if 'created_at' in col or 'updated_at' in col or 'due_date' in col:
            df[col] = df[col].apply(format_datetime)
    
    # Select only specified columns if they exist
    available_cols = [col for col in columns if col in df.columns]
    return df[available_cols] if available_cols else df

def get_status_emoji(status: str) -> str:
    """Get emoji for status"""
    status_emojis = {
        'planning': '📋',
        'in_progress': '🚀',
        'completed': '✅',
        'on_hold': '⏸️',
        'todo': '📝',
        'done': '✅',
    }
    return status_emojis.get(status.lower(), '📄')

def get_priority_emoji(priority: str) -> str:
    """Get emoji for priority"""
    priority_emojis = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🟠',
        'urgent': '🔴'
    }
    return priority_emojis.get(priority.lower(), '⚪')

def create_metric_cards(metrics: Dict[str, Any]):
    """Create metric cards layout"""
    cols = st.columns(len(metrics))
    for i, (label, value) in enumerate(metrics.items()):
        with cols[i]:
            st.metric(label, value)

def confirm_deletion(item_type: str, item_name: str) -> bool:
    """Show confirmation dialog for deletion"""
    return st.checkbox(f"⚠️ Confirm deletion of {item_type}: **{item_name}**")