#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
import tempfile
from pathlib import Path

CONFIG_PATH = Path(os.environ.get('GITBRIDGE_CONFIG', Path.home() / '.gitbridge' / 'config.json'))

def load_config():
    """Load the configuration file"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {"accounts": {}}

def save_config(config):
    """Save the configuration file"""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def add_account(args):
    """Add a new account with a personal access token"""
    config = load_config()
    config['accounts'][args.name] = args.token
    save_config(config)
    print(f"Added account '{args.name}'")

def list_repos(args):
    """List repositories for all configured accounts"""
    config = load_config()
    
    for name, token in config['accounts'].items():
        print(f"Account: {name}")
        
        # Use curl to fetch repositories from GitHub API
        cmd = [
            'curl', '-s',
            '-H', f'Authorization: token {token}',
            'https://api.github.com/user/repos'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            repos = json.loads(result.stdout)
            
            if isinstance(repos, list):
                for repo in repos:
                    print(f"  - {repo['full_name']}")
            else:
                print(f"  Error: Unexpected response format")
        except subprocess.CalledProcessError as e:
            print(f"  Error fetching repos: {e}")
        except json.JSONDecodeError:
            print(f"  Error: Invalid JSON response")
        except Exception as e:
            print(f"  Error: {e}")

def copy_repo(args):
    """Copy a repository from source account to destination account"""
    config = load_config()
    source_token = config['accounts'].get(args.source)
    dest_token = config['accounts'].get(args.dest)
    
    if not source_token or not dest_token:
        print("Source or destination account not found in config.")
        return 1
    
    # Get source repo info
    cmd = [
        'curl', '-s',
        '-H', f'Authorization: token {source_token}',
        f'https://api.github.com/repos/{args.repo}'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        source_repo = json.loads(result.stdout)
        repo_name = source_repo['name']
        
        # Get destination user info
        dest_user_cmd = [
            'curl', '-s',
            '-H', f'Authorization: token {dest_token}',
            'https://api.github.com/user'
        ]
        
        dest_user_result = subprocess.run(dest_user_cmd, capture_output=True, text=True, check=True)
        dest_user = json.loads(dest_user_result.stdout)
        dest_username = dest_user['login']
        
        # Always create a new repo in destination account
        create_cmd = [
            'curl', '-s', '-X', 'POST',
            '-H', f'Authorization: token {dest_token}',
            '-H', 'Content-Type: application/json',
            'https://api.github.com/user/repos',
            '-d', json.dumps({
                'name': repo_name,
                'private': source_repo.get('private', False),
                'description': source_repo.get('description', '')
            })
        ]
        
        # Try to create the repo, but don't fail if it already exists
        create_result = subprocess.run(create_cmd, capture_output=True, text=True)
        create_output = json.loads(create_result.stdout) if create_result.stdout else {}
        
        if 'errors' in create_output and any(e.get('message') == 'name already exists on this account' for e in create_output.get('errors', [])):
            print(f"Destination repo {dest_username}/{repo_name} already exists")
        else:
            print(f"Created destination repo {dest_username}/{repo_name}")
        
        # Clone and push
        with tempfile.TemporaryDirectory() as tmpdir:
            # Clone from source
            clone_url = source_repo['clone_url'].replace("https://", f"https://{source_token}@")
            clone_cmd = ['git', 'clone', clone_url, tmpdir]
            subprocess.run(clone_cmd, check=True, capture_output=True)
            
            # Check if branch exists
            branch_exists = False
            list_branches_cmd = ['git', 'branch', '-a']
            branches_result = subprocess.run(list_branches_cmd, cwd=tmpdir, check=True, capture_output=True, text=True)
            branch_list = branches_result.stdout.splitlines()
            
            for branch in branch_list:
                if args.branch in branch or f'remotes/origin/{args.branch}' in branch:
                    branch_exists = True
                    break
            
            if not branch_exists:
                print(f"Warning: Branch '{args.branch}' not found. Using default branch.")
                checkout_cmd = ['git', 'checkout']
            else:
                checkout_cmd = ['git', 'checkout', args.branch]
                subprocess.run(checkout_cmd, cwd=tmpdir, check=True, capture_output=True)
            
            # Add destination remote and push
            dest_url = f"https://{dest_token}@github.com/{dest_username}/{repo_name}.git"
            subprocess.run(['git', 'remote', 'add', 'dest', dest_url], cwd=tmpdir, check=True)
            
            # Get current branch
            current_branch_cmd = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
            current_branch_result = subprocess.run(current_branch_cmd, cwd=tmpdir, check=True, capture_output=True, text=True)
            current_branch = current_branch_result.stdout.strip()
            
            # Push to destination
            subprocess.run(['git', 'push', '-u', 'dest', current_branch], cwd=tmpdir, check=True)
            
            # Push tags
            tag_cmd = ['git', 'push', '--tags', 'dest']
            subprocess.run(tag_cmd, cwd=tmpdir, capture_output=True)
            
            print(f"Copied {args.repo} to {dest_username}/{repo_name} on branch {current_branch}")
        
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return 1
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON response")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

def delete_repo(args):
    """Delete a repository from an account"""
    config = load_config()
    token = config['accounts'].get(args.account)
    
    if not token:
        print(f"Account '{args.account}' not found in config.")
        return 1
    
    # Parse repo name
    if '/' in args.repo:
        owner, repo_name = args.repo.split('/', 1)
    else:
        # Get user info to determine owner
        user_cmd = [
            'curl', '-s',
            '-H', f'Authorization: token {token}',
            'https://api.github.com/user'
        ]
        user_result = subprocess.run(user_cmd, capture_output=True, text=True, check=True)
        owner = json.loads(user_result.stdout)['login']
        repo_name = args.repo
    
    # Confirm repository exists
    check_cmd = [
        'curl', '-s',
        '-H', f'Authorization: token {token}',
        f'https://api.github.com/repos/{owner}/{repo_name}'
    ]
    
    check_result = subprocess.run(check_cmd, capture_output=True, text=True)
    if check_result.returncode != 0 or 'Not Found' in check_result.stdout:
        print(f"Repository {owner}/{repo_name} not found or not accessible.")
        return 1
    
    # Delete repository
    if not args.force and not args.yes:
        confirm = input(f"Are you sure you want to delete {owner}/{repo_name}? This cannot be undone. (y/N): ")
        if confirm.lower() != 'y':
            print("Deletion cancelled.")
            return 0
    
    delete_cmd = [
        'curl', '-s', '-X', 'DELETE',
        '-H', f'Authorization: token {token}',
        f'https://api.github.com/repos/{owner}/{repo_name}'
    ]
    
    delete_result = subprocess.run(delete_cmd, capture_output=True, text=True)
    
    if delete_result.returncode == 0 and not delete_result.stdout.strip():
        print(f"Successfully deleted repository {owner}/{repo_name}")
        return 0
    else:
        print(f"Failed to delete repository: {delete_result.stderr or delete_result.stdout}")
        return 1

def move_repo(args):
    """Move a repository from one account to another (copy + delete)"""
    # First copy the repository
    copy_args = argparse.Namespace(
        repo=args.repo,
        source=args.source,
        dest=args.dest,
        branch=args.branch
    )
    
    copy_result = copy_repo(copy_args)
    if copy_result != 0:
        print("Failed to copy repository. Aborting move operation.")
        return copy_result
    
    # Then delete the original if copy was successful
    delete_args = argparse.Namespace(
        repo=args.repo,
        account=args.source,
        force=True,
        yes=True
    )
    
    delete_result = delete_repo(delete_args)
    if delete_result != 0:
        print("Warning: Repository was copied but could not be deleted from the source.")
    
    return delete_result

def main():
    parser = argparse.ArgumentParser(description="GitBridge - Git repository manager")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Add account command
    add_parser = subparsers.add_parser('add-account', help='Add a new account')
    add_parser.add_argument('name', help='Account name')
    add_parser.add_argument('token', help='Personal access token')
    
    # List repos command
    list_parser = subparsers.add_parser('list-repos', help='List repositories')
    
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
    
    args = parser.parse_args()
    
    if args.command == 'add-account':
        return add_account(args)
    elif args.command == 'list-repos':
        return list_repos(args)
    elif args.command == 'copy-repo':
        return copy_repo(args)
    elif args.command == 'delete-repo':
        return delete_repo(args)
    elif args.command == 'move-repo':
        return move_repo(args)
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())
