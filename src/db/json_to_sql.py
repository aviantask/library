"""
Convert book JSON data to SQL insert statements.

Usage:
    python json_to_sql.py input.json > inserts.sql
    python json_to_sql.py input.json | sqlite3 library.db

Reads JSON from a file and outputs SQL INSERT statements to stdout.
"""

import json
import re
import sys
from pathlib import Path


def escape_sql(value: str) -> str:
    """Escape a string for SQL (double single quotes)."""
    return value.replace("'", "''")


def extract_year(date_str: str) -> int | None:
    """
    Extract a 4-digit year from a date string.

    Handles formats like:
    - "Apr 07, 2006"
    - "1998"
    - "June 1999"
    - "Dec 31, 2013"
    """
    if not date_str:
        return None
    match = re.search(r'\b(16|17|18|19|20)\d{2}\b', date_str)
    if match:
        return int(match.group())
    return None


def generate_book_sql(book: dict) -> list[str]:
    """Generate SQL statements for a single book."""
    statements = []

    isbn = escape_sql(book.get("isbn", ""))
    title = escape_sql(book.get("title", ""))
    pub_date = escape_sql(book.get("publication_date", ""))
    pub_year = extract_year(book.get("publication_date", ""))
    description = escape_sql(book.get("description", ""))
    ol_key = escape_sql(book.get("open_library_key", ""))

    pub_year_sql = str(pub_year) if pub_year else "NULL"

    # Insert book
    statements.append(
        f"INSERT OR IGNORE INTO books (isbn, title, publication_date, publication_year, description, open_library_key) "
        f"VALUES ('{isbn}', '{title}', '{pub_date}', {pub_year_sql}, '{description}', '{ol_key}');"
    )

    # Insert authors and link to book
    for author in book.get("authors", []):
        author_escaped = escape_sql(author)
        statements.append(
            f"INSERT OR IGNORE INTO authors (name) VALUES ('{author_escaped}');"
        )
        statements.append(
            f"INSERT OR IGNORE INTO book_authors (book_id, author_id) "
            f"SELECT b.id, a.id FROM books b, authors a "
            f"WHERE b.isbn = '{isbn}' AND a.name = '{author_escaped}';"
        )

    # Insert publishers and link to book
    for publisher in book.get("publishers", []):
        publisher_escaped = escape_sql(publisher)
        statements.append(
            f"INSERT OR IGNORE INTO publishers (name) VALUES ('{publisher_escaped}');"
        )
        statements.append(
            f"INSERT OR IGNORE INTO book_publishers (book_id, publisher_id) "
            f"SELECT b.id, p.id FROM books b, publishers p "
            f"WHERE b.isbn = '{isbn}' AND p.name = '{publisher_escaped}';"
        )

    return statements


def json_to_sql(books: list[dict]) -> str:
    """Convert a list of book dicts to SQL statements."""
    lines = [
        "-- Auto-generated SQL insert statements",
        "-- Run with: sqlite3 library.db < inserts.sql",
        "",
        "-- Enable trusted schema for FTS triggers",
        "PRAGMA trusted_schema = ON;",
        "",
        "BEGIN TRANSACTION;",
        ""
    ]

    for book in books:
        isbn = book.get("isbn", "unknown")
        lines.append(f"-- Book: {isbn}")
        lines.extend(generate_book_sql(book))
        lines.append("")

    lines.append("COMMIT;")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python json_to_sql.py <input.json>", file=sys.stderr)
        print("       python json_to_sql.py <input.json> | sqlite3 library.db", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r") as f:
        books = json.load(f)

    if not isinstance(books, list):
        print("Error: JSON must be an array of books", file=sys.stderr)
        sys.exit(1)

    sql = json_to_sql(books)
    print(sql)


if __name__ == "__main__":
    main()
