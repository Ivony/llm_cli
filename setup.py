from setuptools import setup, find_packages

setup(
    name="ai_cli",
    version="0.1.0",
    description="An interactive command-line tool for chatting with LLMs",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "ai-cli=ai_cli.cli:main",
        ],
    },
    install_requires=[
        "prompt_toolkit>=3.0.0",
        "rich>=13.0.0",
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0.0",
        "aiohttp>=3.8.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
