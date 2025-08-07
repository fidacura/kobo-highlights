# setup.py
from setuptools import setup, find_packages

setup(
    name="kobo-highlights",
    version="0.2.0",
    description="A CLI tool to check and extract highlights from Kobo eReaders.",
    url="https://github.com/fidacura/kobo-highlights/",
    author="fidacura",
    author_email="hey@fidacura.net",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "kobo=kobo_highlights.kobo_highlights:main"
        ],
    },
)