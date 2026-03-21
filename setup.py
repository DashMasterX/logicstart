from setuptools import setup, find_packages

setup(
    name="logicstart",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "rich",
        "prompt_toolkit"
    ],
    entry_points={
        "console_scripts": [
            "logicstart=main:main"
        ]
    },
)