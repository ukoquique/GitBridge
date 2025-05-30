"""
GitHub API client module for GitBridge.
Provides a clean interface for interacting with GitHub API.
"""
import json
import subprocess
from typing import Dict, List, Any, Tuple, Optional


class GitHubClient:
    """Client for interacting with GitHub API using curl commands."""
    
    def __init__(self, token: str):
        """Initialize with a GitHub personal access token."""
        self.token = token
        self.base_headers = ['-H', f'Authorization: token {token}']
    
    def _execute_request(self, args: List[str]) -> Tuple[bool, Any]:
        """
        Execute a curl request and return parsed JSON response.
        
        Args:
            args: List of curl command arguments
            
        Returns:
            Tuple of (success, data)
        """
        try:
            result = subprocess.run(args, capture_output=True, text=True, check=False)
            
            # Check if the command was successful
            if result.returncode != 0:
                return False, f"Command failed with exit code {result.returncode}: {result.stderr}"
            
            # Parse JSON response if there is any
            if result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    return True, data
                except json.JSONDecodeError:
                    return False, f"Invalid JSON response: {result.stdout[:100]}..."
            
            # Empty response is considered successful for some operations (like DELETE)
            return True, None
            
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def get_user(self) -> Tuple[bool, Dict[str, Any]]:
        """Get authenticated user information."""
        args = ['curl', '-s', *self.base_headers, 'https://api.github.com/user']
        return self._execute_request(args)
        
    def get_username(self) -> Tuple[bool, str]:
        """Get the username associated with this token.
        
        Returns:
            Tuple of (success, username)
        """
        success, user_data = self.get_user()
        if success and isinstance(user_data, dict) and 'login' in user_data:
            return True, user_data['login']
        return False, ""
    
    def list_repositories(self) -> Tuple[bool, List[Dict[str, Any]]]:
        """List repositories for the authenticated user."""
        args = ['curl', '-s', *self.base_headers, 'https://api.github.com/user/repos']
        return self._execute_request(args)
    
    def get_repository(self, repo_path: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Get repository information.
        
        Args:
            repo_path: Repository path in format "owner/repo"
        """
        args = ['curl', '-s', *self.base_headers, f'https://api.github.com/repos/{repo_path}']
        return self._execute_request(args)
    
    def create_repository(self, name: str, private: bool = False, description: str = "") -> Tuple[bool, Dict[str, Any]]:
        """Create a new repository."""
        data = json.dumps({
            'name': name,
            'private': private,
            'description': description
        })
        
        args = [
            'curl', '-s', '-X', 'POST',
            *self.base_headers,
            '-H', 'Content-Type: application/json',
            'https://api.github.com/user/repos',
            '-d', data
        ]
        
        return self._execute_request(args)
    
    def delete_repository(self, repo_path: str) -> Tuple[bool, Any]:
        """
        Delete a repository.
        
        Args:
            repo_path: Repository path in format "owner/repo"
        """
        # Use -f to treat HTTP errors (4xx/5xx) as curl failures
        args = [
            'curl', '-s', '-f', '-X', 'DELETE',
            *self.base_headers,
            f'https://api.github.com/repos/{repo_path}'
        ]
        # Execute delete and provide token permission suggestion on failure
        success, data = self._execute_request(args)
        if not success:
            err_msg = data if isinstance(data, str) else ''
            return False, f"{err_msg}. Check the token permissions."
        return True, data
    
    def repository_exists(self, repo_path: str) -> bool:
        """Check if a repository exists and is accessible."""
        success, data = self.get_repository(repo_path)
        # If the request failed, repository doesn't exist or inaccessible
        if not success:
            return False
        # GitHub returns JSON {'message':'Not Found',...} on 404, so check message
        if isinstance(data, dict) and data.get('message', '').lower().startswith('not found'):
            return False
        return True
    
    def list_repository_contents(self, repo_path: str, path: str = "") -> Tuple[bool, Any]:
        """
        List contents of a repository at given path.
        """
        if path:
            url = f"https://api.github.com/repos/{repo_path}/contents/{path}"
        else:
            url = f"https://api.github.com/repos/{repo_path}/contents"
        args = ['curl', '-s', *self.base_headers, url]
        return self._execute_request(args)


def parse_repository_path(repo_path: str, default_owner: Optional[str] = None) -> Tuple[str, str]:
    """
    Parse a repository path into owner and repo name.
    
    Args:
        repo_path: Repository path, can be "owner/repo" or just "repo"
        default_owner: Default owner to use if not specified in repo_path
        
    Returns:
        Tuple of (owner, repo_name)
        
    Raises:
        ValueError: If repo_path doesn't contain owner and default_owner is not provided
    """
    if '/' in repo_path:
        return repo_path.split('/', 1)
    elif default_owner:
        return default_owner, repo_path
    else:
        raise ValueError(f"Repository path '{repo_path}' does not contain owner and no default owner provided")
