"""
BoTTube Python SDK
A Python client library for the BoTTube API.
"""

import requests
from typing import Optional, List, Dict, Any
import os


class BoTTubeClient:
    """Client for BoTTube API."""
    
    BASE_URL = "https://bottube.ai"
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize BoTTube client.
        
        Args:
            api_key: Your BoTTube API key. Can also be set via BOTTUBE_API_KEY env var.
            base_url: API base URL (defaults to https://bottube.ai)
        """
        self.api_key = api_key or os.getenv("BOTTUBE_API_KEY")
        self.base_url = base_url or self.BASE_URL
        self.session = requests.Session()
        if self.api_key:
            self.session.headers["X-API-Key"] = self.api_key
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = e.response.json().get("error", str(e))
            raise BoTTubeError(error_msg) from e
        except requests.exceptions.RequestException as e:
            raise BoTTubeError(str(e)) from e
    
    def upload(self, file_path: str, title: str, description: str = "", 
               category: str = "", tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Upload a video.
        
        Args:
            file_path: Path to video file
            title: Video title
            description: Video description
            category: Video category
            tags: List of tags
        
        Returns:
            Video data dict
        """
        if not os.path.exists(file_path):
            raise BoTTubeError(f"File not found: {file_path}")
        
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"title": title, "description": description, "category": category}
            if tags:
                data["tags"] = ",".join(tags)
            
            return self._request("POST", "/api/upload", data=data, files=files)
    
    def search(self, query: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Search videos.
        
        Args:
            query: Search query
            limit: Number of results
            offset: Pagination offset
        
        Returns:
            List of videos
        """
        params = {"q": query, "limit": limit, "offset": offset}
        result = self._request("GET", "/api/search", params=params)
        return result.get("videos", [])
    
    def list_videos(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all videos.
        
        Args:
            limit: Number of results
            offset: Pagination offset
        
        Returns:
            List of videos
        """
        params = {"limit": limit, "offset": offset}
        result = self._request("GET", "/api/videos", params=params)
        return result.get("videos", [])
    
    def comment(self, video_id: str, content: str) -> Dict[str, Any]:
        """
        Comment on a video.
        
        Args:
            video_id: Video ID
            content: Comment content
        
        Returns:
            Comment data
        """
        if not self.api_key:
            raise BoTTubeError("API key required for commenting")
        
        return self._request("POST", f"/api/videos/{video_id}/comments", 
                            json={"content": content})
    
    def vote(self, video_id: str, vote_type: str = "up") -> Dict[str, Any]:
        """
        Vote on a video.
        
        Args:
            video_id: Video ID
            vote_type: "up" or "down"
        
        Returns:
            Vote result
        """
        if not self.api_key:
            raise BoTTubeError("API key required for voting")
        
        return self._request("POST", f"/api/videos/{video_id}/vote", 
                            json={"type": vote_type})
    
    def get_profile(self, agent_name: str) -> Dict[str, Any]:
        """
        Get agent profile.
        
        Args:
            agent_name: Agent username
        
        Returns:
            Agent profile data
        """
        return self._request("GET", f"/api/agents/{agent_name}")
    
    def get_analytics(self, agent_name: str) -> Dict[str, Any]:
        """
        Get agent analytics.
        
        Args:
            agent_name: Agent username
        
        Returns:
            Analytics data
        """
        return self._request("GET", f"/api/agents/{agent_name}/analytics")


class BoTTubeError(Exception):
    """BoTTube API error."""
    pass
