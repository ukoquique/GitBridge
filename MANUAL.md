# GitBridge Manual

GitBridge is a tool for managing multiple Git repositories across different accounts and services. It helps you synchronize, organize, and manage repositories between GitHub accounts. It provides both a command-line interface and a graphical user interface for ease of use.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Command-Line Interface](#command-line-interface)
4. [Graphical User Interface](#graphical-user-interface)
5. [Architecture](#architecture)
6. [Use Cases](#use-cases)
7. [Troubleshooting](#troubleshooting)

## Installation

GitBridge is a Python-based tool that requires no external dependencies. You can install it directly from the source code:

```bash
# Clone the repository
git clone https://github.com/ukoquique/GitBridge.git
cd GitBridge

# Install in development mode
pip install -e .
```

## Configuration

GitBridge uses a configuration file to store your GitHub account tokens. The default location is `~/.gitbridge/config.json`.

### Manual Configuration

You can manually create or edit the configuration file:

```json
{
  "accounts": {
    "github_personal": "your_personal_github_token",
    "github_work": "your_work_github_token"
  }
}
```

### Using the CLI

You can add accounts using the command line:

```bash
# Using the full CLI (requires dependencies)
python -m gitbridge add-account github_personal <TOKEN>

# Using the simple CLI (no dependencies)
python /path/to/GitBridge/gitbridge/simple_cli.py add-account github_personal <TOKEN>
```

### GitHub Tokens

To create a GitHub personal access token:

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Click "Generate new token"
3. Select the following scopes:
   - `repo` (Full control of private repositories)
   - `read:user` (Read user information)
4. Generate the token and copy it
5. Add it to GitBridge using the commands above

## Command-Line Interface

GitBridge supports the following commands:

### Add Account

Add a new GitHub account with a personal access token:

```bash
gitbridge add-account <ACCOUNT_NAME> <TOKEN>
```

Example:
```bash
gitbridge add-account github_personal YOUR_GITHUB_TOKEN
```

### List Repositories

List all repositories from all configured accounts:

```bash
gitbridge list-repos
```

This will display all repositories for each account in your configuration.

### Copy Repository

Copy a repository from one account to another:

```bash
gitbridge copy-repo <OWNER/REPO> --source <SOURCE_ACCOUNT> --dest <DEST_ACCOUNT> [--branch <BRANCH>]
```

Example:
```bash
gitbridge copy-repo HectorCorbellini/lovableTranslator --source HectorCorbellini --dest ukoquique
```

This will:
1. Create a new repository in the destination account (if it doesn't exist)
2. Clone the source repository
3. Push all content to the destination repository
4. Push all tags to the destination repository

### Delete Repository

Delete a repository from an account:

```bash
gitbridge delete-repo <OWNER/REPO> --account <ACCOUNT_NAME> [--force] [--yes]
```

Options:
- `--force` or `-f`: Skip confirmation prompt
- `--yes` or `-y`: Assume yes to confirmation prompt

Example:
```bash
gitbridge delete-repo HectorCorbellini/old-project --account HectorCorbellini
```

This will permanently delete the repository after confirmation.

### Move Repository

Move a repository from one account to another (copy + delete):

```bash
gitbridge move-repo <OWNER/REPO> --source <SOURCE_ACCOUNT> --dest <DEST_ACCOUNT> [--branch <BRANCH>]
```

Example:
```bash
gitbridge move-repo HectorCorbellini/portfolio-vercel --source HectorCorbellini --dest ukoquique
```

This will:
1. Copy the repository to the destination account
2. Delete the repository from the source account

If the copy succeeds but the deletion fails, a warning will be displayed.

## Graphical User Interface

GitBridge provides a user-friendly graphical interface for all operations. You can launch it with:

```bash
python -m gitbridge.gui_app
```

### Standalone Launcher

For easier access, GitBridge now includes a standalone launcher script. You can run the application using any of these methods:

```bash
# Method 1: Run the launcher directly (recommended)
./gitbridge_app.py

# Method 2: Run the launcher with Python
python3 gitbridge_app.py

# Method 3: Original module method
python3 -m gitbridge.gui_app
```

The standalone launcher provides these benefits:
- Simpler to use and remember
- Can be added to desktop shortcuts or application menus
- Includes proper error handling
- Works from any directory (when installed properly)

### GUI Features

#### Add Account Tab

Allows you to add new GitHub accounts and manage existing ones:

- Add new accounts with name and token
- View all existing accounts with masked tokens for security
- Delete accounts with a single click
- Automatic duplicate account detection (prevents adding the same GitHub account twice)

#### List Repos Tab

Displays all repositories across your accounts:

- Shows repositories grouped by account
- Includes repository full names
- Refresh button to update the list

#### Copy Repo Tab

Copy repositories between accounts:

- Select source and destination accounts from dropdowns
- Specify repository name and branch
- Handles repository creation in the destination account

#### Delete Repo Tab

Delete repositories from an account:

- Select account from dropdown
- Enter repository name
- Confirmation dialog to prevent accidental deletion

#### Move Repo Tab

Move repositories from one account to another:

- Select source and destination accounts
- Enter repository name
- Performs copy followed by delete

#### View Repo Tab

Browse repository contents:

- Select account and repository from dropdowns
- View files and folders in the repository
- Refresh to update the view

## Architecture

GitBridge follows clean code principles with a modular architecture designed for maintainability, testability, and extensibility.

### Core Components

- **config_manager.py**: Handles loading, saving, and managing configuration
  - `ConfigManager`: Manages account tokens and configuration settings

- **github_api.py**: Provides a clean interface to GitHub API
  - `GitHubClient`: Handles API requests to GitHub
  - Helper functions for parsing repository paths

- **git_operations.py**: Handles Git operations
  - `GitOperations`: Low-level Git command execution
  - `GitRepoSync`: High-level repository synchronization

- **commands.py**: Implements command business logic
  - Command handler classes for each operation
  - Separation of concerns between CLI and business logic

- **cli_app.py**: Command-line interface
  - Argument parsing and command routing
  - User-friendly error handling
  
- **gui_app.py**: Graphical user interface
  - Tkinter-based UI with tabs for different operations
  - Event-driven architecture
  - Reuses the same business logic as the CLI

### Design Principles

1. **Single Responsibility Principle**: Each module and class has a single responsibility
2. **Dependency Inversion**: High-level modules don't depend on low-level modules
3. **Error Handling**: Consistent error handling throughout the codebase
4. **Testability**: Components are designed to be easily testable
5. **No External Dependencies**: Uses only standard Python libraries
6. **Code Reuse**: Both CLI and GUI use the same underlying business logic
7. **User Experience**: Intuitive interfaces for both command-line and graphical users

## Use Cases

### Managing Multiple GitHub Identities

If you have separate GitHub accounts for personal and work projects, GitBridge helps you manage and synchronize repositories between them.

Example workflow:
1. Create a personal project under your personal account
2. When ready to share with work colleagues, copy it to your work account:
   ```bash
   python /path/to/GitBridge/gitbridge/simple_cli.py copy-repo personal_user/project --source github_personal --dest github_work
   ```

### Backing Up Repositories

You can use GitBridge to create backups of your repositories across different accounts:

```bash
python /path/to/GitBridge/gitbridge/simple_cli.py copy-repo important_user/important_project --source github_main --dest github_backup
```

### Collaborative Development

When collaborating with others who have their own GitHub accounts:

1. List their repositories:
   ```bash
   python /path/to/GitBridge/gitbridge/simple_cli.py list-repos
   ```

2. Copy a specific repository to your account:
   ```bash
   python /path/to/GitBridge/gitbridge/simple_cli.py copy-repo collaborator/project --source collaborator_account --dest my_account
   ```

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

1. Verify your token has the correct permissions (needs `repo` scope)
2. Check that the token is correctly added to the configuration
3. Ensure the token hasn't expired

### Repository Not Found

If a repository can't be found:

1. Check that the repository exists in the source account
2. Verify you have access to the repository
3. Ensure you're using the correct format: `owner/repo`

### Branch Issues

If you encounter branch-related issues:

1. Specify the correct branch name with `--branch`
2. If the branch doesn't exist, GitBridge will use the default branch

## Future Features

GitBridge is under development, with plans to add:

1. **Translation Support**: Auto-translate README files between languages
2. **Repository Tagging**: Add custom tags to organize repositories
3. **Cross-Platform Support**: Add support for GitLab, Bitbucket, etc.
4. **Web Dashboard**: A web-based UI for managing repositories
5. **Automated Synchronization**: Keep repositories in sync automatically
