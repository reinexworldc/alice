from setuptools import setup, find_packages

setup(
    name="alice-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["pydantic", "openai", "prompt_toolkit"],
    entry_points={
        "console_scripts": [
            "alice=cli.main:main",
        ],
    },
    python_requires=">=3.7",
)
