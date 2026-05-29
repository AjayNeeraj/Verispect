import os
from setuptools import setup, find_packages

readme = ""
if os.path.exists("README.md"):
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()

setup(
    name="verispect-sdk",
    version="0.1.0",
    description="AI drift detection and compliance monitoring — wraps any OpenAI-compatible client with one line.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Verispect",
    author_email="support@verispectai.com",
    url="https://verispectai.com",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "httpx>=0.24.0",
        "sentence-transformers>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "openai>=1.0.0",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai drift detection compliance openai llm monitoring eu-ai-act",
)
