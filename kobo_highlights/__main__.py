#!/usr/bin/env python3
"""
main entry point for kobo_highlights package when run as module.
"""

import sys
import os

# add the parent directory to path so we can import from kobo_highlights.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import and run the main function from the cli script
from kobo_highlights import main

if __name__ == "__main__":
    main()


# Update setup.py to fix entry points
from setuptools import setup, find_packages

setup(
    name='kobo-highlights',
    version='0.1',
    description="A tool to extract highlights from Kobo devices.",
    url="https://github.com/fidacura/kobo-highlights/",
    author="fidacura",
    author_email="hello@fidacura.xyz",
    license='MIT',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "kobo-highlights=kobo_highlights.main:main",  # Fixed this line
        ],
    },
)


# Alternative: Update pyproject.toml (more modern)
[project.scripts]
kobo-highlights = "kobo_highlights.main:main"  # Point to the main function