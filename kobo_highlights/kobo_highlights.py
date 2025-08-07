"""
Main entry point for kobo_highlights package with Git-style subcommands.
"""

import sys
import os
import argparse
from datetime import datetime
from typing import Optional


def get_kobo_path(provided_path: Optional[str] = None) -> str:
    """Get Kobo path from various sources in priority order."""
    if provided_path:
        return provided_path
    
    # check environment variable
    env_path = os.environ.get('KOBO_PATH')
    if env_path:
        return env_path
    
    # check config file
    config_file = os.path.expanduser('~/.kobo-highlights')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                saved_path = f.read().strip()
                if saved_path:
                    return saved_path
        except:
            pass  # Ignore config file errors
    
    # fall back to default
    from . import DEFAULT_KOBO_PATH
    return DEFAULT_KOBO_PATH


def save_kobo_path(path: str) -> None:
    """Save Kobo path to config file."""
    config_file = os.path.expanduser('~/.kobo-highlights')
    try:
        with open(config_file, 'w') as f:
            f.write(path)
        print(f"✓ Saved Kobo path: {path}")
        print(f"✓ Saved to: {config_file}")
    except Exception as e:
        print(f"Error saving path: {e}", file=sys.stderr)
        sys.exit(1)


def validate_kobo_path(kobo_path: str) -> None:
    """Validate that Kobo path exists and contains database."""
    if not os.path.exists(kobo_path):
        print(f"Error: Kobo path not found: {kobo_path}", file=sys.stderr)
        print("Hint: Use 'kobo backup set-path /path/to/kobo' to save your Kobo path", file=sys.stderr)
        print("      or set KOBO_PATH environment variable", file=sys.stderr)
        sys.exit(1)


def auto_generate_filename(base_name: str, extension: str) -> str:
    """Generate a filename with timestamp if no filename provided."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"


def resolve_book_filter(extractor, book_arg: str):
    """Resolve book argument to book_id, handling both numbers and titles."""
    if not book_arg:
        return None, None
    
    # try to parse as number first
    try:
        book_num = int(book_arg)
        books = extractor.list_books_with_highlights_numbered()
        for num, book_id, title, author in books:
            if num == book_num:
                return book_id, None  # return book_id for filtering
        print(f"Error: Book number {book_num} not found. Use 'kobo list' to see available books.", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        # NaN, treat as title
        return None, book_arg  # Return book_title for filtering


def cmd_help(args):
    """Handle help subcommand - shows same as --help."""
    # get main parser and print its help
    parser = create_main_parser()
    parser.print_help()


def cmd_backup(args):
    """Handle backup subcommand."""
    from .highlights_extractor import KoboHighlightExtractor
    
    # handle set-path
    if args.set_path:
        save_kobo_path(args.set_path)
        return
    
    # get and validate kobo path
    kobo_path = get_kobo_path(args.kobo_path)
    validate_kobo_path(kobo_path)
    
    try:
        extractor = KoboHighlightExtractor(kobo_path)
        
        # generate filename if not provided
        output_file = args.output
        if not output_file:
            output_file = auto_generate_filename("kobo_backup", "sqlite")
        elif not output_file.endswith('.sqlite'):
            output_file += '.sqlite'
        
        extractor.backup_database(output_file)
        print(f"✓ Database backed up to {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args):
    """Handle list subcommand."""
    from .highlights_extractor import KoboHighlightExtractor
    
    kobo_path = get_kobo_path(args.kobo_path)
    validate_kobo_path(kobo_path)
    
    try:
        extractor = KoboHighlightExtractor(kobo_path)
        books = extractor.list_books_with_highlights_numbered()
        
        print("Available books with highlights:")
        print("-" * 60)
        for num, _, title, author in books:
            print(f"{num:2d}. {title}")
            print(f"    by {author}")
            print()
        print("Use --book <number> or --book \"title\" to filter exports")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_count(args):
    """Handle count subcommand."""
    from .highlights_extractor import KoboHighlightExtractor
    
    kobo_path = get_kobo_path(args.kobo_path)
    validate_kobo_path(kobo_path)
    
    try:
        extractor = KoboHighlightExtractor(kobo_path)
        count_info = extractor.get_highlight_count()
        print(f"Total highlights: {count_info['total_highlights']}")
        print(f"Books with highlights: {count_info['books_with_highlights']}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def cmd_show(args):
    """Handle show subcommand - display highlights to screen."""
    from .highlights_extractor import KoboHighlightExtractor
    
    kobo_path = get_kobo_path(args.kobo_path)
    validate_kobo_path(kobo_path)
    
    try:
        extractor = KoboHighlightExtractor(kobo_path)
        
        # resolve book filter
        book_id, book_title = resolve_book_filter(extractor, args.book)
        
        # parse date filters
        date_from = datetime.strptime(args.from_date, "%Y-%m-%d") if args.from_date else None
        date_to = datetime.strptime(args.to_date, "%Y-%m-%d") if args.to_date else None
        
        # get highlights with filters
        highlights = extractor.get_highlights(book_id, book_title, date_from, date_to)
        
        if not highlights:
            print("No highlights found with given criteria.")
            return
        
        # print highlights using same format as TXT export
        print_highlights_to_screen(highlights)
        print(f"\n📚 Found {len(highlights)} highlights")
        
    except ValueError as e:
        if "time data" in str(e):
            print("Error: Date format must be YYYY-MM-DD", file=sys.stderr)
        else:
            print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def print_highlights_to_screen(highlights):
    """Print highlights to screen using same format as TXT export."""
    if not highlights:
        return
        
    # print header with book information
    first_highlight = highlights[0]
    print("-" * 75)
    print(f"VolumeID: {first_highlight[1]}")
    print(f"Book Title: {first_highlight[4]}")
    print(f"Author: {first_highlight[5]}")
    print("-" * 75)
    print()
    
    # print individual highlights with separators
    for i, highlight in enumerate(highlights):
        print(f"BookmarkID: {highlight[0]}")
        print(f"Date Created: {highlight[6]}")
        print("–")
        print(f"Highlight:")
        print(f"{highlight[2]}")
        
        # add separator between highlights (not after last one)
        if i < len(highlights) - 1:
            print()
            print("-" * 75)
            print()
        else:
            print()


def cmd_export(args):
    """Handle export subcommand."""
    from .highlights_extractor import KoboHighlightExtractor
    
    kobo_path = get_kobo_path(args.kobo_path)
    validate_kobo_path(kobo_path)
    
    try:
        extractor = KoboHighlightExtractor(kobo_path)
        
        # resolve book filter
        book_id, book_title = resolve_book_filter(extractor, args.book)
        
        # parse date filters
        date_from = datetime.strptime(args.from_date, "%Y-%m-%d") if args.from_date else None
        date_to = datetime.strptime(args.to_date, "%Y-%m-%d") if args.to_date else None
        
        # get highlights with filters
        highlights = extractor.get_highlights(book_id, book_title, date_from, date_to)
        
        if not highlights:
            print("No highlights found with given criteria.")
            return
        
        # generate filename if not provided
        output_file = args.output
        if not output_file:
            base_name = "kobo_highlights"
            if book_title:
                # clean title for filename
                clean_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                base_name = f"highlights_{clean_title.replace(' ', '_')}"
            elif book_id:
                # clean book_id path for filename
                clean_book_id = book_id.split('/')[-1].replace('.epub', '')  # get filename without path/extension
                clean_book_id = "".join(c for c in clean_book_id if c.isalnum() or c in (' ', '-', '_')).rstrip()
                base_name = f"highlights_{clean_book_id.replace(' ', '_')}"
            output_file = auto_generate_filename(base_name, args.format)
        elif not output_file.endswith(f'.{args.format}'):
            output_file += f'.{args.format}'
        
        # export to specified format
        if args.format == 'txt':
            extractor.export_txt(highlights, output_file)
        elif args.format == 'json':
            extractor.export_json(highlights, output_file)
        elif args.format == 'csv':
            extractor.export_csv(highlights, output_file)
        
        print(f"✓ Exported {len(highlights)} highlights to {output_file}")
        
    except ValueError as e:
        if "time data" in str(e):
            print("Error: Date format must be YYYY-MM-DD", file=sys.stderr)
        else:
            print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def create_main_parser():
    """Create main argument parser."""
    parser = argparse.ArgumentParser(
        description="Extract and manage highlights from Kobo devices",
        prog="kobo"
    )
    
    # global arguments
    parser.add_argument(
        "--kobo-path", 
        help="Path to Kobo device (overrides saved path)"
    )
    
    # create subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # help subcommand (add FIRST)
    help_parser = subparsers.add_parser('help', help='Show help information')
    help_parser.set_defaults(func=cmd_help)
    
    # backup subcommand
    backup_parser = subparsers.add_parser('backup', help='Backup Kobo database')
    backup_parser.add_argument(
        'output', 
        nargs='?', 
        help='Output filename (auto-generated if not provided)'
    )
    backup_parser.add_argument(
        'set-path', 
        help='Save Kobo path for future use'
    )
    backup_parser.set_defaults(func=cmd_backup)
    
    # list subcommand (with alias)
    list_parser = subparsers.add_parser('list', aliases=['ls'], help='List books with highlights')
    list_parser.set_defaults(func=cmd_list)
    
    # count subcommand  
    count_parser = subparsers.add_parser('count', help='Show highlight statistics')
    count_parser.set_defaults(func=cmd_count)
    
    # show subcommand
    show_parser = subparsers.add_parser('show', help='Display highlights on screen')
    show_parser.add_argument(
        '--book', 
        help='Filter by book number (from list) or partial title match'
    )
    show_parser.add_argument(
        '--from', 
        dest='from_date',
        help='Filter highlights from this date (YYYY-MM-DD)'
    )
    show_parser.add_argument(
        '--to', 
        dest='to_date',
        help='Filter highlights to this date (YYYY-MM-DD)'
    )
    show_parser.set_defaults(func=cmd_show)
    
    # export subcommand
    export_parser = subparsers.add_parser('export', help='Export highlights')
    export_parser.add_argument(
        'format', 
        choices=['txt', 'json', 'csv'], 
        help='Export format'
    )
    export_parser.add_argument(
        'output', 
        nargs='?', 
        help='Output filename (auto-generated if not provided)'
    )
    export_parser.add_argument(
        '--book', 
        help='Filter by book number (from list) or partial title match'
    )
    export_parser.add_argument(
        '--from', 
        dest='from_date',
        help='Filter highlights from this date (YYYY-MM-DD)'
    )
    export_parser.add_argument(
        '--to', 
        dest='to_date',
        help='Filter highlights to this date (YYYY-MM-DD)'
    )
    export_parser.set_defaults(func=cmd_export)
    
    return parser


def main():
    """Main entry point with Git-style subcommands."""
    parser = create_main_parser()
    
    # parse and execute
    args = parser.parse_args()
    
    # if no command is provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # execute command
    args.func(args)


if __name__ == "__main__":
    main()