# GitBridge

Code repository organizer and synchronizer.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Set config file (optional):

```bash
export GITBRIDGE_CONFIG=~/.gitbridge/config.json
```

Add accounts:

```bash
python -m gitbridge add-account github_personal <TOKEN>
python -m gitbridge add-account github_work <TOKEN>
```

List repositories:

```bash
python -m gitbridge list-repos
```

Copy repository:

```bash
python -m gitbridge copy-repo <owner/repo or repo> --source github_personal --dest github_work --branch main
