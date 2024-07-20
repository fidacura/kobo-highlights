import sqlite3
import json
import os
import csv
import shutil
from typing import List, Tuple, Dict
from datetime import datetime
import configparser

class KoboHighlightExtractor:
    def __init__(self, kobo_path: str, config_file: str = None):
        self.config = self.load_config(config_file)
        self.db_path = os.path.join(kobo_path, '.kobo', 'KoboReader.sqlite')

    def load_config(self, config_file: str) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        if config_file and os.path.exists(config_file):
            config.read(config_file)
        return config

    def get_highlights(self, book_id: str = None, book_title: str = None, date_from: datetime = None, date_to: datetime = None) -> List[Tuple[int, str, str, str, str, str, str]]:
        query = '''
            SELECT b.BookmarkID, b.VolumeID, b.Text, b.ContentID, c.Title, c.Attribution, b.DateCreated
            FROM Bookmark b
            JOIN content c ON b.VolumeID = c.ContentID
            WHERE b.Type = 'highlight'
        '''
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
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def list_books_with_highlights(self) -> List[Tuple[str, str, str]]:
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
            return cursor.fetchall()

    def get_highlight_count(self) -> Dict[str, int]:
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
        with open(output_file, 'w', encoding='utf-8') as f:
            for highlight in highlights:
                f.write(f"BookmarkID: {highlight[0]}\n")
                f.write(f"VolumeID: {highlight[1]}\n")
                f.write(f"Highlight: {highlight[2]}\n")
                f.write(f"ContentID: {highlight[3]}\n")
                f.write(f"Book Title: {highlight[4]}\n")
                f.write(f"Author: {highlight[5]}\n")
                f.write(f"Date Created: {highlight[6]}\n\n")

    def export_json(self, highlights: List[Tuple[int, str, str, str, str, str, str]], output_file: str) -> None:
        highlights_data = [
            {
                "BookmarkID": h[0],
                "VolumeID": h[1],
                "Text": h[2],
                "ContentID": h[3],
                "BookTitle": h[4],
                "Author": h[5],
                "DateCreated": h[6]
            } for h in highlights
        ]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(highlights_data, f, ensure_ascii=False, indent=2)

    def export_csv(self, highlights: List[Tuple[int, str, str, str, str, str, str]], output_file: str) -> None:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["BookmarkID", "VolumeID", "Text", "ContentID", "BookTitle", "Author", "DateCreated"])
            writer.writerows(highlights)

    def export_sqlite(self, highlights: List[Tuple[int, str, str, str, str, str, str]], output_file: str) -> None:
        with sqlite3.connect(output_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS highlights (
                    BookmarkID INTEGER PRIMARY KEY,
                    VolumeID TEXT,
                    Text TEXT,
                    ContentID TEXT,
                    BookTitle TEXT,
                    Author TEXT,
                    DateCreated TEXT
                )
            ''')
            cursor.executemany('''
                INSERT INTO highlights (BookmarkID, VolumeID, Text, ContentID, BookTitle, Author, DateCreated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', highlights)

    def backup_database(self, backup_path: str) -> None:
        try:
            shutil.copy2(self.db_path, backup_path)
        except IOError as e:
            raise Exception(f"Backup error: {e}")