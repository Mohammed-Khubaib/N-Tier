import os
# from typing import Optional

class ClientConfig:
    def __init__(self):
        self.api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.timeout: int = int(os.getenv("API_TIMEOUT", "30"))
        
    def get_endpoint(self, path: str) -> str:
        """Get full endpoint URL"""
        return f"{self.api_base_url.rstrip('/')}/{path.lstrip('/')}"

config = ClientConfig()