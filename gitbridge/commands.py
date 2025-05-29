"""
Command handlers for GitBridge CLI.
Implements the business logic for each command.
"""
import sys
from typing import Dict, List, Any, Optional, Tuple

from gitbridge.config_manager import ConfigManager
from gitbridge.github_api import GitHubClient, parse_repository_path
from gitbridge.git_operations import GitRepoSync


class CommandHandler:
    """Base class for command handlers."""
    
    def __init__(self, config: ConfigManager):
        """Initialize with configuration manager."""
        self.config = config
    
    def execute(self, args: Any) -> int:
        """
        Execute the command.
        
        Args:
            args: Command arguments
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        raise NotImplementedError("Subclasses must implement execute()")


class AddAccountCommand(CommandHandler):
    """Handler for add-account command."""
    
    def execute(self, args: Any) -> int:
        """Add a new account with a personal access token."""
        if self.config.add_account(args.name, args.token):
            print(f"Added account '{args.name}'")
            return 0
        else:
            print(f"Failed to add account '{args.name}'")
            return 1


class ListReposCommand(CommandHandler):
    """Handler for list-repos command."""
    
    def execute(self, args: Any) -> int:
        """List repositories for all configured accounts."""
        accounts = self.config.get_accounts()
        if not accounts:
            print("No accounts configured. Use add-account to add an account.")
            return 1
        
        success = False
        for name, token in accounts.items():
            print(f"Account: {name}")
            client = GitHubClient(token)
            success_repos, repos = client.list_repositories()
            
            if success_repos and isinstance(repos, list):
                success = True
                for repo in repos:
                    print(f"  - {repo['full_name']}")
            else:
                print(f"  Error fetching repositories: {repos}")
        
        return 0 if success else 1


class CopyRepoCommand(CommandHandler):
    """Handler for copy-repo command."""
    
    def execute(self, args: Any) -> int:
        """Copy a repository from source account to destination account."""
        # Get tokens
        source_token = self.config.get_account_token(args.source)
        dest_token = self.config.get_account_token(args.dest)
        
        if not source_token or not dest_token:
            print("Source or destination account not found in config.")
            return 1
        
        # Create API clients
        source_client = GitHubClient(source_token)
        dest_client = GitHubClient(dest_token)
        
        # Get source repo info
        success, source_repo = source_client.get_repository(args.repo)
        if not success:
            print(f"Error accessing source repository {args.repo}: {source_repo}")
            return 1
        
        repo_name = source_repo['name']
        
        # Get destination user info
        success, dest_user = dest_client.get_user()
        if not success:
            print(f"Error accessing destination account: {dest_user}")
            return 1
        
        dest_username = dest_user['login']
        dest_repo_path = f"{dest_username}/{repo_name}"
        
        # Create destination repo if it doesn't exist
        if dest_client.repository_exists(dest_repo_path):
            print(f"Destination repo {dest_repo_path} already exists")
        else:
            success, result = dest_client.create_repository(
                repo_name,
                private=source_repo.get('private', False),
                description=source_repo.get('description', '')
            )
            
            if success:
                print(f"Created destination repo {dest_repo_path}")
            else:
                print(f"Failed to create destination repo: {result}")
                return 1
        
        # Prepare URLs with authentication
        source_url = source_repo['clone_url'].replace("https://", f"https://{source_token}@")
        dest_url = f"https://{dest_token}@github.com/{dest_username}/{repo_name}.git"
        
        # Copy repository
        success, message, branch = GitRepoSync.copy_repository(
            source_url, 
            dest_url, 
            args.branch
        )
        
        if success:
            print(f"Copied {args.repo} to {dest_repo_path} on branch {branch}")
            return 0
        else:
            print(f"Failed to copy repository: {message}")
            return 1


class DeleteRepoCommand(CommandHandler):
    """Handler for delete-repo command."""
    
    def execute(self, args: Any) -> int:
        """Delete a repository from an account."""
        # Get token
        token = self.config.get_account_token(args.account)
        if not token:
            print(f"Account '{args.account}' not found in config.")
            return 1
        
        client = GitHubClient(token)
        
        # Get user info if needed
        try:
            if '/' in args.repo:
                repo_path = args.repo
            else:
                success, user_info = client.get_user()
                if not success:
                    print(f"Error accessing user information: {user_info}")
                    return 1
                repo_path = f"{user_info['login']}/{args.repo}"
        except Exception as e:
            print(f"Error parsing repository path: {e}")
            return 1
        
        # Check if repository exists
        if not client.repository_exists(repo_path):
            print(f"Repository {repo_path} not found or not accessible.")
            return 1
        
        # Confirm deletion
        if not args.force and not args.yes:
            confirm = input(f"Are you sure you want to delete {repo_path}? This cannot be undone. (y/N): ")
            if confirm.lower() != 'y':
                print("Deletion cancelled.")
                return 0
        
        # Delete repository
        success, result = client.delete_repository(repo_path)
        
        if success:
            print(f"Successfully deleted repository {repo_path}")
            return 0
        else:
            print(f"Failed to delete repository: {result}")
            return 1


class MoveRepoCommand(CommandHandler):
    """Handler for move-repo command."""
    
    def execute(self, args: Any) -> int:
        """Move a repository from one account to another (copy + delete)."""
        # First copy the repository
        copy_handler = CopyRepoCommand(self.config)
        copy_result = copy_handler.execute(args)
        
        if copy_result != 0:
            print("Failed to copy repository. Aborting move operation.")
            return copy_result
        
        # Then delete the original
        delete_args = type('DeleteArgs', (), {
            'repo': args.repo,
            'account': args.source,
            'force': True,
            'yes': True
        })
        
        delete_handler = DeleteRepoCommand(self.config)
        delete_result = delete_handler.execute(delete_args)
        
        if delete_result != 0:
            print("Warning: Repository was copied but could not be deleted from the source.")
        
        return delete_result


def get_command_handler(command: str, config: ConfigManager) -> Optional[CommandHandler]:
    """
    Get the appropriate command handler for a command.
    
    Args:
        command: Command name
        config: Configuration manager
        
    Returns:
        Command handler or None if command not found
    """
    handlers = {
        'add-account': AddAccountCommand,
        'list-repos': ListReposCommand,
        'copy-repo': CopyRepoCommand,
        'delete-repo': DeleteRepoCommand,
        'move-repo': MoveRepoCommand
    }
    
    handler_class = handlers.get(command)
    if handler_class:
        return handler_class(config)
    return None
