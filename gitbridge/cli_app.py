#!/usr/bin/env python3
"""
Command-line interface for GitBridge.
Provides a user-friendly interface for managing Git repositories across accounts.
"""
import sys
import argparse
from typing import List, Optional

from gitbridge.config_manager import ConfigManager
from gitbridge.commands import get_command_handler


def setup_parsers() -> argparse.ArgumentParser:
    """
    Set up command-line argument parsers.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="GitBridge - Git repository manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gitbridge add-account github_personal <TOKEN>
  gitbridge list-repos
  gitbridge copy-repo owner/repo --source github_personal --dest github_work
  gitbridge move-repo owner/repo --source github_personal --dest github_work
  gitbridge delete-repo owner/repo --account github_personal
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Add account command
    add_parser = subparsers.add_parser('add-account', help='Add a new account')
    add_parser.add_argument('name', help='Account name')
    add_parser.add_argument('token', help='Personal access token')
    
    # List repos command
    subparsers.add_parser('list-repos', help='List repositories')
    
    # Copy repo command
    copy_parser = subparsers.add_parser('copy-repo', help='Copy a repository')
    copy_parser.add_argument('repo', help='Repository name (owner/repo)')
    copy_parser.add_argument('--source', required=True, help='Source account name')
    copy_parser.add_argument('--dest', required=True, help='Destination account name')
    copy_parser.add_argument('--branch', default='main', help='Branch to copy')
    
    # Delete repo command
    delete_parser = subparsers.add_parser('delete-repo', help='Delete a repository')
    delete_parser.add_argument('repo', help='Repository name (owner/repo)')
    delete_parser.add_argument('--account', required=True, help='Account name')
    delete_parser.add_argument('--force', '-f', action='store_true', help='Force deletion without confirmation')
    delete_parser.add_argument('--yes', '-y', action='store_true', help='Assume yes to confirmation prompt')
    
    # Move repo command
    move_parser = subparsers.add_parser('move-repo', help='Move a repository (copy + delete)')
    move_parser.add_argument('repo', help='Repository name (owner/repo)')
    move_parser.add_argument('--source', required=True, help='Source account name')
    move_parser.add_argument('--dest', required=True, help='Destination account name')
    move_parser.add_argument('--branch', default='main', help='Branch to copy')
    
    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command-line arguments (optional, defaults to sys.argv[1:])
        
    Returns:
        Exit code
    """
    parser = setup_parsers()
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 1
    
    config = ConfigManager()
    handler = get_command_handler(parsed_args.command, config)
    
    if handler:
        try:
            return handler.execute(parsed_args)
        except Exception as e:
            print(f"Error executing command: {e}")
            return 1
    else:
        print(f"Unknown command: {parsed_args.command}")
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
