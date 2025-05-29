import typer
from gitbridge.config import Config
from github import Github
from git import Repo
import tempfile

typing = typer.Typer()

@typing.command()
def add_account(name: str, token: str):
    """Add a new account with a personal access token"""
    config = Config.load()
    config.data['accounts'][name] = token
    config.save()
    typer.echo(f"Added account '{name}'")

@typing.command()
def list_repos():
    """List repositories for all configured accounts"""
    config = Config.load()
    for name, token in config.data['accounts'].items():
        typer.echo(f"Account: {name}")
        g = Github(token)
        try:
            user = g.get_user()
            repos = user.get_repos()
            for r in repos:
                typer.echo(f"  - {r.full_name}")
        except Exception as e:
            typer.echo(f"  Error fetching repos for {name}: {e}")

@typing.command()
def copy_repo(repo: str, source: str, dest: str, branch: str = 'main'):
    """Copy a repository from source account to destination account"""
    config = Config.load()
    source_token = config.data['accounts'].get(source)
    dest_token = config.data['accounts'].get(dest)
    if not source_token or not dest_token:
        typer.echo("Source or destination account not found in config.")
        raise typer.Exit(code=1)
    source_g = Github(source_token)
    dest_g = Github(dest_token)
    if '/' in repo:
        full_name = repo
    else:
        full_name = f"{source_g.get_user().login}/{repo}"
    try:
        src_repo = source_g.get_repo(full_name)
    except Exception as e:
        typer.echo(f"Error accessing source repo {full_name}: {e}")
        raise typer.Exit(code=1)
    dest_user = dest_g.get_user()
    repo_name = src_repo.name
    dest_full_name = f"{dest_user.login}/{repo_name}"
    try:
        dest_repo = dest_g.get_repo(dest_full_name)
        typer.echo(f"Destination repo {dest_full_name} already exists.")
    except Exception:
        dest_repo = dest_user.create_repo(repo_name, private=src_repo.private, description=src_repo.description)
        typer.echo(f"Created destination repo {dest_full_name}.")
    with tempfile.TemporaryDirectory() as tmpdir:
        clone_url = src_repo.clone_url.replace("https://", f"https://{source_token}@")
        repo_local = Repo.clone_from(clone_url, tmpdir, branch=branch)
        dest_url = dest_repo.clone_url.replace("https://", f"https://{dest_token}@")
        repo_local.create_remote("dest", dest_url)
        repo_local.git.push("dest", branch)
        repo_local.git.push("--tags", "dest")
        typer.echo(f"Copied {full_name} to {dest_full_name} on branch {branch}.")

def main():
    typing()
