import requests
import streamlit as st
from typing import Dict, Any, Optional
from client.config import config

class APIClient:
    def __init__(self):
        self.base_url = config.api_base_url
        self.timeout = config.timeout
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make HTTP request to API"""
        url = config.get_endpoint(endpoint)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            if response.status_code == 204:  # No content for DELETE
                return {"success": True}
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure the FastAPI server is running!")
            return None
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                st.error("❌ Resource not found!")
            elif e.response.status_code == 400:
                try:
                    error_detail = e.response.json().get("detail", "Bad request")
                    st.error(f"❌ {error_detail}")
                except:
                    st.error("❌ Bad request")
            else:
                st.error(f"❌ HTTP Error: {e.response.status_code}")
            return None
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            return None
    
    # User endpoints
    def get_users(self, skip: int = 0, limit: int = 100) -> Optional[Any]:
        return self._make_request("GET", f"users/?skip={skip}&limit={limit}")
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        return self._make_request("GET", f"users/{user_id}")
    
    def create_user(self, user_data: Dict) -> Optional[Dict]:
        return self._make_request("POST", "users/", json=user_data)
    
    def update_user(self, user_id: int, user_data: Dict) -> Optional[Dict]:
        return self._make_request("PUT", f"users/{user_id}", json=user_data)
    
    def delete_user(self, user_id: int) -> Optional[Dict]:
        return self._make_request("DELETE", f"users/{user_id}")
    
    # Project endpoints
    def get_projects(self, skip: int = 0, limit: int = 100) -> Optional[Any]:
        return self._make_request("GET", f"projects/?skip={skip}&limit={limit}")
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        return self._make_request("GET", f"projects/{project_id}")
    
    def create_project(self, project_data: Dict) -> Optional[Dict]:
        return self._make_request("POST", "projects/", json=project_data)
    
    def update_project(self, project_id: int, project_data: Dict) -> Optional[Dict]:
        return self._make_request("PUT", f"projects/{project_id}", json=project_data)
    
    def delete_project(self, project_id: int) -> Optional[Dict]:
        return self._make_request("DELETE", f"projects/{project_id}")
    
    # Task endpoints
    def get_tasks(self, skip: int = 0, limit: int = 100) -> Optional[Any]:
        return self._make_request("GET", f"tasks/?skip={skip}&limit={limit}")
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        return self._make_request("GET", f"tasks/{task_id}")
    
    def create_task(self, task_data: Dict) -> Optional[Dict]:
        return self._make_request("POST", "tasks/", json=task_data)
    
    def update_task(self, task_id: int, task_data: Dict) -> Optional[Dict]:
        return self._make_request("PUT", f"tasks/{task_id}", json=task_data)
    
    def delete_task(self, task_id: int) -> Optional[Dict]:
        return self._make_request("DELETE", f"tasks/{task_id}")

# Create global API client instance
api_client = APIClient()