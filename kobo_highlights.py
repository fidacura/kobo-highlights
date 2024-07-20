#!/usr/bin/env python3
import argparse
import sys
from kobo_highlights import KoboHighlightExtractor, DEFAULT_KOBO_PATH
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Extract highlights from Kobo devices")
    parser.add_argument("kobo_path", nargs='?', default=DEFAULT_KOBO_PATH, help=f"Path to the Kobo device (default: {DEFAULT_KOBO_PATH})")
    parser.add_argument("--backup", help="Backup the Kobo database to the specified file")
    parser.add_argument("--list-books", action="store_true", help="List books with highlights")
    parser.add_argument("--count", action="store_true", help="Print highlight count information")
    parser.add_argument("--book-id", help="Filter by book ID")
    parser.add_argument("--book-title", help="Filter by book title")
    parser.add_argument("--date-from", help="Filter highlights from this date (YYYY-MM-DD)")
    parser.add_argument("--date-to", help="Filter highlights to this date (YYYY-MM-DD)")
    parser.add_argument("--txt", help="Export to TXT file")
    parser.add_argument("--json", help="Export to JSON file")
    parser.add_argument("--csv", help="Export to CSV file")
    parser.add_argument("--sqlite", help="Export to SQLite database")

    args = parser.parse_args()

    try:
        extractor = KoboHighlightExtractor(args.kobo_path)

        if args.backup:
            extractor.backup_database(args.backup)
            print(f"Database backed up to {args.backup}")
            return

        if args.list_books:
            books = extractor.list_books_with_highlights()
            for book in books:
                print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}")
            return

        if args.count:
            count_info = extractor.get_highlight_count()
            print(f"Total highlights: {count_info['total_highlights']}")
            print(f"Books with highlights: {count_info['books_with_highlights']}")
            return

        # Convert date strings to datetime objects
        date_from = datetime.strptime(args.date_from, "%Y-%m-%d") if args.date_from else None
        date_to = datetime.strptime(args.date_to, "%Y-%m-%d") if args.date_to else None

        # Get highlights
        highlights = extractor.get_highlights(args.book_id, args.book_title, date_from, date_to)

        if not highlights:
            print("No highlights found with the given criteria.")
            return

        if args.txt:
            extractor.export_txt(highlights, args.txt)
            print(f"Exported to {args.txt}")
        if args.json:
            extractor.export_json(highlights, args.json)
            print(f"Exported to {args.json}")
        if args.csv:
            extractor.export_csv(highlights, args.csv)
            print(f"Exported to {args.csv}")
        if args.sqlite:
            extractor.export_sqlite(highlights, args.sqlite)
            print(f"Exported to {args.sqlite}")

        if not any([args.txt, args.json, args.csv, args.sqlite]):
            # If no export format is specified, print the highlights to console
            for highlight in highlights:
                print(f"Book: {highlight[4]}")
                print(f"Author: {highlight[5]}")
                print(f"Highlight: {highlight[2]}")
                print(f"Date: {highlight[6]}")
                print("---")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()