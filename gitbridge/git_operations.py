"""
Git operations module for GitBridge.
Provides functionality for Git operations like cloning, pushing, etc.
"""
import os
import subprocess
import tempfile
from typing import List, Tuple, Optional


class GitOperations:
    """Class for handling Git operations."""
    
    @staticmethod
    def run_git_command(args: List[str], cwd: Optional[str] = None) -> Tuple[bool, str]:
        """
        Run a Git command and return the result.
        
        Args:
            args: Git command arguments
            cwd: Working directory for the command
            
        Returns:
            Tuple of (success, output)
        """
        try:
            result = subprocess.run(
                args, 
                cwd=cwd, 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, f"Command failed: {result.stderr}"
        except Exception as e:
            return False, f"Error executing Git command: {str(e)}"
    
    @staticmethod
    def clone_repository(url: str, target_dir: str, branch: Optional[str] = None) -> Tuple[bool, str]:
        """
        Clone a Git repository.
        
        Args:
            url: Repository URL
            target_dir: Target directory
            branch: Branch to clone (optional)
            
        Returns:
            Tuple of (success, message)
        """
        cmd = ['git', 'clone']
        if branch:
            cmd.extend(['--branch', branch])
        cmd.extend([url, target_dir])
        
        return GitOperations.run_git_command(cmd)
    
    @staticmethod
    def add_remote(remote_name: str, url: str, cwd: str) -> Tuple[bool, str]:
        """Add a Git remote."""
        cmd = ['git', 'remote', 'add', remote_name, url]
        return GitOperations.run_git_command(cmd, cwd)
    
    @staticmethod
    def push(remote: str, branch: str, cwd: str, set_upstream: bool = False) -> Tuple[bool, str]:
        """Push to a Git remote."""
        cmd = ['git', 'push']
        if set_upstream:
            cmd.append('-u')
        cmd.extend([remote, branch])
        
        return GitOperations.run_git_command(cmd, cwd)
    
    @staticmethod
    def push_tags(remote: str, cwd: str) -> Tuple[bool, str]:
        """Push tags to a Git remote."""
        cmd = ['git', 'push', '--tags', remote]
        return GitOperations.run_git_command(cmd, cwd)
    
    @staticmethod
    def checkout(branch: Optional[str], cwd: str) -> Tuple[bool, str]:
        """Checkout a branch."""
        cmd = ['git', 'checkout']
        if branch:
            cmd.append(branch)
        
        return GitOperations.run_git_command(cmd, cwd)
    
    @staticmethod
    def get_current_branch(cwd: str) -> Tuple[bool, str]:
        """Get the current branch name."""
        cmd = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
        return GitOperations.run_git_command(cmd, cwd)
    
    @staticmethod
    def list_branches(cwd: str) -> Tuple[bool, List[str]]:
        """List all branches."""
        success, output = GitOperations.run_git_command(['git', 'branch', '-a'], cwd)
        if success:
            branches = [b.strip() for b in output.splitlines()]
            return True, branches
        return False, []
    
    @staticmethod
    def branch_exists(branch: str, cwd: str) -> bool:
        """Check if a branch exists."""
        success, branches = GitOperations.list_branches(cwd)
        if not success:
            return False
            
        for b in branches:
            # Check for local branch or remote branch
            if branch == b.strip('* ') or f'remotes/origin/{branch}' in b:
                return True
                
        return False


class GitRepoSync:
    """Class for synchronizing Git repositories."""
    
    @staticmethod
    def copy_repository(
        source_url: str, 
        dest_url: str, 
        branch: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Copy a repository from source to destination.
        
        Args:
            source_url: Source repository URL with auth token
            dest_url: Destination repository URL with auth token
            branch: Branch to copy (optional)
            
        Returns:
            Tuple of (success, message, branch_name)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Clone repository
            success, message = GitOperations.clone_repository(source_url, tmpdir)
            if not success:
                return False, f"Failed to clone repository: {message}", None
                
            # Check if branch exists and checkout
            if branch and GitOperations.branch_exists(branch, tmpdir):
                success, message = GitOperations.checkout(branch, tmpdir)
                if not success:
                    return False, f"Failed to checkout branch {branch}: {message}", None
            else:
                if branch:
                    print(f"Warning: Branch '{branch}' not found. Using default branch.")
                
            # Get current branch
            success, current_branch = GitOperations.get_current_branch(tmpdir)
            if not success:
                return False, "Failed to determine current branch", None
                
            # Add destination remote
            success, message = GitOperations.add_remote('dest', dest_url, tmpdir)
            if not success:
                return False, f"Failed to add remote: {message}", None
                
            # Push to destination
            success, message = GitOperations.push('dest', current_branch, tmpdir, True)
            if not success:
                return False, f"Failed to push to destination: {message}", None
                
            # Push tags
            GitOperations.push_tags('dest', tmpdir)
            
            return True, "Repository copied successfully", current_branch
