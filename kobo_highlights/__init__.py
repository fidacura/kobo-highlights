# kobo_highlights
"""
kobo_highlights - A tool to extract highlights from Kobo devices.
This package provides a simple way to extract highlights from Kobo e-readers
and export them to various formats including TXT, JSON, CSV, and SQLite.
"""

# Version of the kobo_highlights package
__version__ = "0.1.0"

# Import the main class so it can be imported directly from the package
from .highlights_extractor import KoboHighlightExtractor

# List of public objects in this package
__all__ = ["KoboHighlightExtractor"]

# Default Kobo path
DEFAULT_KOBO_PATH = "/Volumes/KOBOeReader"  # Kobo's default path in macOS