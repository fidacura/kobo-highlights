# Kobo Highlights Extractor

A Python tool to extract and export highlights from Kobo e-readers.

## Features

- Extract highlights from Kobo devices
- Export highlights to TXT, JSON, CSV, and SQLite formats
- List books with highlights
- Count total highlights and books with highlights
- Backup Kobo database

## Setup

1. Clone this repository:

```bash
git clone https://github.com/fidacura/kobo-highlights.git
cd kobo-highlights
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

You can use the script directly from the command line:

1. Backup the Kobo database:

```bash
python kobo-highlights.py --backup backup.sqlite
```

2. List books with highlights:

```bash
python kobo-highlights.py --list-books
```

3. Get highlight count:

```bash
python kobo-highlights.py --count
```

4. Export highlights (use one or more of --txt, --json, --csv, --sqlite):

```bash
python kobo-highlights.py --txt highlights.txt --json highlights.json
```

5. Export highlights for a specific book:

```bash
python kobo-highlights.py --book-id [book_id] --csv book_highlights.csv
```

6. Export highlights within a date range:

```bash
python kobo-highlights.py --date-from YYYY-MM-DD --date-to YYYY-MM-DD --json date_range_highlights.json
```

For more options, run:

```bash
python kobo-highlights.py --help
```

## Testing

To run the tests:
python -m unittest discover tests

## Contributing

Contributions are welcome! Feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
