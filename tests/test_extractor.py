import os
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
from kobo_highlights.highlights_extractor import KoboHighlightExtractor

class TestKoboHighlightExtractor(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.kobo_path = os.path.join(self.test_dir, 'kobo')
        os.makedirs(os.path.join(self.kobo_path, '.kobo'))
        
        self.sample_highlights = [
            (1, 'VolumeID1', 'This is a highlight', 'content1', 'Book1', 'Author1', '2023-01-01 12:00:00'),
            (2, 'VolumeID2', 'Another highlight', 'content2', 'Book2', 'Author2', '2023-01-02 13:00:00'),
        ]

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    @patch('sqlite3.connect')
    def test_get_highlights(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = self.sample_highlights
        mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        extractor = KoboHighlightExtractor(self.kobo_path)
        highlights = extractor.get_highlights()

        self.assertEqual(highlights, self.sample_highlights)
        mock_cursor.execute.assert_called_once()

    @patch('sqlite3.connect')
    def test_get_highlights_with_filters(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = self.sample_highlights
        mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        extractor = KoboHighlightExtractor(self.kobo_path)
        
        extractor.get_highlights(book_id='VolumeID1')
        mock_cursor.execute.assert_called()

        date_from = datetime(2023, 1, 1)
        date_to = datetime(2023, 1, 2)
        extractor.get_highlights(date_from=date_from, date_to=date_to)
        mock_cursor.execute.assert_called()

    @patch('sqlite3.connect')
    def test_list_books_with_highlights(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [('VolumeID1', 'Book1', 'Author1'), ('VolumeID2', 'Book2', 'Author2')]
        mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        extractor = KoboHighlightExtractor(self.kobo_path)
        books = extractor.list_books_with_highlights()

        self.assertEqual(len(books), 2)
        self.assertEqual(books[0], ('VolumeID1', 'Book1', 'Author1'))
        self.assertEqual(books[1], ('VolumeID2', 'Book2', 'Author2'))

    @patch('sqlite3.connect')
    def test_get_highlight_count(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (10, 5)
        mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        extractor = KoboHighlightExtractor(self.kobo_path)
        count_info = extractor.get_highlight_count()

        self.assertEqual(count_info['total_highlights'], 10)
        self.assertEqual(count_info['books_with_highlights'], 5)

    def test_export_txt(self):
        extractor = KoboHighlightExtractor(self.kobo_path)
        m = mock_open()
        with patch('builtins.open', m):
            extractor.export_txt(self.sample_highlights, 'output.txt')

        m.assert_called_once_with('output.txt', 'w', encoding='utf-8')
        handle = m()
        handle.write.assert_any_call("BookmarkID: 1\n")
        handle.write.assert_any_call("VolumeID: VolumeID1\n")
        handle.write.assert_any_call("Highlight: This is a highlight\n")
        handle.write.assert_any_call("ContentID: content1\n")
        handle.write.assert_any_call("Book Title: Book1\n")
        handle.write.assert_any_call("Author: Author1\n")
        handle.write.assert_any_call("Date Created: 2023-01-01 12:00:00\n\n")

    def test_export_json(self):
        extractor = KoboHighlightExtractor(self.kobo_path)
        m = mock_open()
        with patch('builtins.open', m), patch('json.dump') as mock_json_dump:
            extractor.export_json(self.sample_highlights, 'output.json')

        m.assert_called_once_with('output.json', 'w', encoding='utf-8')
        mock_json_dump.assert_called_once()
        args, kwargs = mock_json_dump.call_args
        self.assertEqual(len(args[0]), 2)  # Two highlights
        self.assertEqual(args[0][0]['BookmarkID'], 1)
        self.assertEqual(args[0][1]['BookmarkID'], 2)
        self.assertEqual(args[0][0]['BookTitle'], 'Book1')
        self.assertEqual(args[0][1]['BookTitle'], 'Book2')
        self.assertEqual(args[0][0]['DateCreated'], '2023-01-01 12:00:00')
        self.assertEqual(args[0][1]['DateCreated'], '2023-01-02 13:00:00')

    def test_export_csv(self):
        extractor = KoboHighlightExtractor(self.kobo_path)
        m = mock_open()
        with patch('builtins.open', m), patch('csv.writer') as mock_csv_writer:
            extractor.export_csv(self.sample_highlights, 'output.csv')

        m.assert_called_once_with('output.csv', 'w', newline='', encoding='utf-8')
        mock_csv_writer.return_value.writerow.assert_called_with(["BookmarkID", "VolumeID", "Text", "ContentID", "BookTitle", "Author", "DateCreated"])
        mock_csv_writer.return_value.writerows.assert_called_with(self.sample_highlights)

    @patch('sqlite3.connect')
    def test_export_sqlite(self, mock_connect):
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        extractor = KoboHighlightExtractor(self.kobo_path)
        extractor.export_sqlite(self.sample_highlights, 'output.db')

        mock_cursor.execute.assert_called()
        mock_cursor.executemany.assert_called()

    @patch('os.path.exists')
    @patch('configparser.ConfigParser.read')
    def test_load_config(self, mock_read, mock_exists):
        config_path = os.path.join(self.test_dir, 'config.ini')
        mock_exists.return_value = True  # Simulate that the config file exists
        
        KoboHighlightExtractor(self.kobo_path, config_path)
        
        mock_exists.assert_called_once_with(config_path)
        mock_read.assert_called_once_with(config_path)

    @patch('shutil.copy2')
    def test_backup_database(self, mock_copy):
        extractor = KoboHighlightExtractor(self.kobo_path)
        backup_path = os.path.join(self.test_dir, 'backup.sqlite')
        extractor.backup_database(backup_path)
        mock_copy.assert_called_once_with(extractor.db_path, backup_path)

if __name__ == '__main__':
    unittest.main(verbosity=2)