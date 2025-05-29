from setuptools import setup, find_packages

setup(
    name="gitbridge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer[all]==0.9.0",
        "PyGithub==1.58.2",
        "GitPython==3.1.32",
    ],
    entry_points={
        "console_scripts": [
            "gitbridge=gitbridge.cli:main",
        ],
    },
)
