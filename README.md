# kobo-highlights extractor

A tool to extract and export highlights (and database) from Kobo e-readers.

## Features

- Extract highlights from Kobo devices
- Export highlights to TXT, JSON, CSV, and SQLite formats
- List books with highlights
- Count total highlights and books with highlights
- Backup Kobo database

## Setup

1. clone the repo

```bash
git clone https://github.com/fidacura/kobo-highlights.git
cd kobo-highlights
```

2. create and activate venv

```bash
python -m venv venv
source venv/bin/activate
```

3. install deps

```bash
pip install -r requirements.txt
```

## Usage

You can use the script directly from the command line:

```bash
# show all available options
python kobo_highlights.py --help

# backup your kobo database
python kobo_highlights.py --backup backup.sqlite

# list all books with highlights
python kobo_highlights.py --list-books

# see how many highlights you have
python kobo_highlights.py --count

# export your highlights
python kobo_highlights.py --txt highlights.txt --json highlights.json

# export highlights from a specific book
python kobo_highlights.py --book-id [book_id] --csv book_highlights.csv

# export highlights from a date range
python kobo_highlights.py --date-from 2024-01-01 --date-to 2024-02-01 --json recent.json
```

For more options, run:

```bash
python kobo_highlights.py --help
```

## Testing

To run the tests:
python -m unittest discover tests
