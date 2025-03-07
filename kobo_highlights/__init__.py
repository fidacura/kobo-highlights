# kobo_highlights
"""
kobo-highlights - A tool to extract highlights from Kobo devices.
"""

# Version of the kobo_highlights package
__version__ = "0.1.0"

# Import the main class so it can be imported directly from the package
from .highlights_extractor import KoboHighlightExtractor

# List of public objects in this package
__all__ = ["KoboHighlightExtractor"]

# Default Kobo path
DEFAULT_KOBO_PATH = "/Volumes/KOBOeReader"  # Kobo's default path in macOS