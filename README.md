# GitBridge

A clean, modular code repository organizer and synchronizer that helps manage multiple accounts and projects across Git services.

## Features

- **No External Dependencies**: Uses standard Python libraries and system commands
- **Account Management**: Add and manage multiple GitHub accounts
- **Repository Operations**:
  - List repositories across accounts
  - Copy repositories between accounts
  - Delete repositories
  - Move repositories (copy + delete)
- **Clean Code Architecture**:
  - Modular design with separation of concerns
  - Reusable components
  - Consistent error handling

## Installation

```bash
# Clone the repository
git clone https://github.com/ukoquique/GitBridge.git
cd GitBridge

# Install in development mode
pip install -e .
```

## Usage

Set config file location (optional):

```bash
export GITBRIDGE_CONFIG=~/.gitbridge/config.json
```

### Account Management

Add GitHub accounts:

```bash
gitbridge add-account github_personal YOUR_GITHUB_TOKEN
gitbridge add-account github_work YOUR_GITHUB_TOKEN
```

### Repository Operations

List all repositories:

```bash
gitbridge list-repos
```

Copy a repository between accounts:

```bash
gitbridge copy-repo owner/repo --source github_personal --dest github_work --branch main
```

Move a repository (copy + delete):

```bash
gitbridge move-repo owner/repo --source github_personal --dest github_work
```

Delete a repository:

```bash
gitbridge delete-repo owner/repo --account github_personal
```

## Architecture

GitBridge follows clean code principles with a modular architecture:

- **config_manager.py**: Configuration loading and management
- **github_api.py**: GitHub API client
- **git_operations.py**: Git operations and repository synchronization
- **commands.py**: Command handlers implementing business logic
- **cli_app.py**: Command-line interface and entry point
