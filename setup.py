# setup.py
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
            "kobo-highlights=kobo_highlights.__main__:main",
        ],
    },
)