from setuptools import setup, find_packages

setup(
    name="gitbridge",
    version="0.1.0",
    description="Git repository organizer and synchronizer",
    author="GitBridge Team",
    packages=find_packages(),
    install_requires=[
        # No external dependencies required for core functionality
    ],
    entry_points={
        "console_scripts": [
            "gitbridge=gitbridge.cli_app:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
)
