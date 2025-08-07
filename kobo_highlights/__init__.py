"""
kobo-highlights - A CLI tool to check and extract highlights from Kobo eReaders.

- kobo backup [output.sqlite]
- kobo list (or kobo ls)  
- kobo count
- kobo export txt/json/csv [filename]
"""

__version__ = "0.2.0"

# import main class for library usage
from .highlights_extractor import KoboHighlightExtractor

# import main function for CLI entry point
from .kobo_highlights import main

# default kobo path (macOS)
DEFAULT_KOBO_PATH = "/Volumes/KOBOeReader"

__all__ = ["KoboHighlightExtractor", "main", "DEFAULT_KOBO_PATH"]