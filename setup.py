# setup.py

from setuptools import setup, find_packages

setup(
    name="logicstart",
    version="2.0.0",
    description="IDE LogicStart Pro Max: Python em português, segurança avançada e execução segura",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Felipe Silva",
    author_email="seuemail@exemplo.com",
    url="https://github.com/seuusuario/logicstart",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.0.0",
        "prompt_toolkit>=3.0.40",
        "flask>=2.3.0",
        "flask-cors>=3.0.10",
        "flask-dance>=6.5.0",
        "pymongo>=4.5.0"
    ],
    extras_require={
        "dev": ["pytest", "black", "mypy"]
    },
    entry_points={
        "console_scripts": [
            "logicstart=main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: IDE"
    ],
    include_package_data=True,
)
