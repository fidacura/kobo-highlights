import sqlite3
import json
import os
import csv
import shutil
from typing import List, Tuple, Dict, Optional
from datetime import datetime
import configparser

class KoboHighlightExtractor:
    def __init__(self, kobo_path: str, config_file: str = None):
        # add simple path validation
        if not os.path.exists(kobo_path):
            raise FileNotFoundError(f"Kobo path not found: {kobo_path}")
        
        self.config = self.load_config(config_file)
        self.db_path = os.path.join(kobo_path, '.kobo', 'KoboReader.sqlite')
        
        # add database validation
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Kobo database not found: {self.db_path}")

    def load_config(self, config_file: str) -> configparser.ConfigParser:
        """Load configuration from file if it exists."""
        config = configparser.ConfigParser()
        if config_file and os.path.exists(config_file):
            config.read(config_file)
        return config
    
    def _clean_file_path(self, path: str) -> str:
        """Remove unnecessary file path information."""
        prefix = "file:///mnt/onboard/"
        if path.startswith(prefix):
            return path[len(prefix):]
        return path

    def get_highlights(self, book_id: str = None, book_title: str = None, date_from: datetime = None, date_to: datetime = None) -> List[Tuple[int, str, str, str, str, str, str]]:
        """Get highlights with optional filters."""
        # base query to grab all highlight info 
        query = '''
            SELECT b.BookmarkID, b.VolumeID, b.Text, b.ContentID, c.Title, c.Attribution, b.DateCreated
            FROM Bookmark b
            JOIN content c ON b.VolumeID = c.ContentID
            WHERE b.Type = 'highlight'
        '''
        
        # build up query filters based on user request
        params = []
        if book_id:
            query += ' AND b.VolumeID = ?'
            params.append(book_id)
        elif book_title:
            query += ' AND c.Title LIKE ?'
            params.append(f'%{book_title}%')
        if date_from:
            query += ' AND b.DateCreated >= ?'
            params.append(date_from.strftime('%Y-%m-%d'))
        if date_to:
            query += ' AND b.DateCreated <= ?'
            params.append(date_to.strftime('%Y-%m-%d'))
        
        # Add ORDER BY at the end
        query += ' ORDER BY b.DateCreated ASC'
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()

        # clean up those funky kobo paths in results for display
        cleaned_results = [
            (
                h[0],                           # BookmarkID
                self._clean_file_path(h[1]),    # VolumeID (cleaned)
                h[2],                           # Text
                self._clean_file_path(h[3]),    # ContentID (cleaned)
                h[4],                           # Title
                h[5] or "Unknown Author",       # Attribution (handle null)
                h[6]                            # DateCreated
            ) for h in results
        ]

        return cleaned_results

    def list_books_with_highlights(self) -> List[Tuple[str, str, str]]:
        """Get a list of all books that have highlights."""
        query = '''
            SELECT DISTINCT c.ContentID, c.Title, c.Attribution
            FROM Bookmark b
            JOIN content c ON b.VolumeID = c.ContentID
            WHERE b.Type = 'highlight'
            ORDER BY c.Title
        '''
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()

        # clean file paths in results for display
        cleaned_results = [
            (
                self._clean_file_path(b[0]),    # ContentID (cleaned)
                b[1],                           # Title
                b[2] or "Unknown Author"        # Attribution (handle null)
            ) for b in results
        ]

        return cleaned_results
    
    def list_books_with_highlights_numbered(self) -> List[Tuple[int, str, str, str]]:
        """List books with simple numeric IDs for user convenience.
        
        IMPORTANT: Returns ORIGINAL uncleaned VolumeID for proper database queries.
        """
        query = '''
            SELECT DISTINCT b.VolumeID, c.Title, c.Attribution
            FROM Bookmark b
            JOIN content c ON b.VolumeID = c.ContentID
            WHERE b.Type = 'highlight'
            ORDER BY c.Title
        '''
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()

        # return numbered list with ORIGINAL VolumeID (not clean)
        numbered_results = []
        for i, (volume_id, title, author) in enumerate(results):
            numbered_results.append((
                i + 1,                          # Number
                volume_id,                      # ORIGINAL VolumeID (uncleaned)
                title,                          # Title
                author or "Unknown Author"      # Attribution
            ))

        return numbered_results

    def get_book_by_number(self, book_num: int) -> Optional[str]:
        """Get book VolumeID by book number from the numbered list. 
        
        This fixes bug where book filtering by number wasn't working.
        Returns ORIGINAL VolumeID for proper database queries.
        """
        books = self.list_books_with_highlights_numbered()
        for num, volume_id, title, author in books:
            if num == book_num:
                return volume_id  # return ORIGINAL VolumeID
        return None

    def get_highlight_count(self) -> Dict[str, int]:
        """Count total highlights and books with highlights."""
        query = '''
            SELECT 
                COUNT(*) as total_highlights,
                COUNT(DISTINCT VolumeID) as books_with_highlights
            FROM Bookmark
            WHERE Type = 'highlight'
        '''
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            return {
                'total_highlights': result[0],
                'books_with_highlights': result[1]
            }

    def export_txt(self, highlights: List[Tuple[int, str, str, str, str, str, str]], output_file: str) -> None:
        """Export highlights to a simple text file with improved formatting."""
        if not highlights:
            return
            
        with open(output_file, 'w', encoding='utf-8') as f:
            # write header with book information (it's the same for all highlights)
            first_highlight = highlights[0]
            f.write("-" * 75 + "\n")
            f.write(f"VolumeID: {first_highlight[1]}\n")
            f.write(f"Book Title: {first_highlight[4]}\n")
            f.write(f"Author: {first_highlight[5]}\n")
            f.write("-" * 75 + "\n\n")
            
            # write individual highlights with separators
            for i, highlight in enumerate(highlights):
                f.write(f"BookmarkID: {highlight[0]}\n")
                f.write(f"Date Created: {highlight[6]}\n")
                f.write("–\n")
                f.write(f"Highlight:\n{highlight[2]}\n")
                
                # add separator between highlights (not after last one)
                if i < len(highlights) - 1:
                    f.write("\n" + "-" * 75 + "\n\n")
                else:
                    f.write("\n")

    def export_json(self, highlights: List[Tuple[int, str, str, str, str, str, str]], output_file: str) -> None:
        """Export highlights to JSON format with logical field ordering."""
        highlights_data = [
            {
                "BookmarkID": h[0],
                "VolumeID": h[1],
                "BookTitle": h[4],
                "Author": h[5],
                "DateCreated": h[6],
                "Highlight": h[2]
            } for h in highlights
        ]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(highlights_data, f, ensure_ascii=False, indent=2)

    def export_csv(self, highlights: List[Tuple[int, str, str, str, str, str, str]], output_file: str) -> None:
        """Export highlights to CSV format with logical column ordering."""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar='\\')
            writer.writerow(["BookmarkID", "VolumeID", "BookTitle", "Author", "DateCreated", "Highlight"])
            for highlight in highlights:
                # replace newlines with space to keep CSV structure intact
                cleaned_text = highlight[2].replace('\n', ' ').replace('\r', '')
                writer.writerow([
                    highlight[0],
                    highlight[1],
                    highlight[4],
                    highlight[5],
                    highlight[6],
                    cleaned_text
                ])

    def backup_database(self, backup_path: str) -> None:
        """Create a backup copy of Kobo database file."""
        try:
            shutil.copy2(self.db_path, backup_path)
        except IOError as e:
            raise Exception(f"Backup error: {e}")