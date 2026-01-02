"""
Library search module.

Provides search functionality against the library database.
Uses FTS5 for fuzzy text matching on titles and authors.
"""

import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = Path(__file__).parent / "db" / "library.db"


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Open a database connection with row factory enabled."""
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def search_by_title(conn: sqlite3.Connection, term: str) -> list[sqlite3.Row]:
    """
    Search books by title using FTS5 fuzzy matching.

    Returns books with their authors.
    """
    query = """
        SELECT
            b.id,
            b.isbn,
            b.title,
            b.publication_year,
            GROUP_CONCAT(DISTINCT a.name) AS authors
        FROM books_fts fts
        JOIN books b ON b.id = fts.rowid
        LEFT JOIN book_authors ba ON ba.book_id = b.id
        LEFT JOIN authors a ON a.id = ba.author_id
        WHERE books_fts MATCH ?
        GROUP BY b.id
        ORDER BY rank
    """
    # FTS5 query syntax: use * for prefix matching
    fts_term = f'"{term}"*'
    return conn.execute(query, (fts_term,)).fetchall()


def search_by_author(conn: sqlite3.Connection, term: str) -> list[sqlite3.Row]:
    """
    Search books by author name using FTS5 fuzzy matching.

    Returns books with their authors.
    """
    query = """
        SELECT
            b.id,
            b.isbn,
            b.title,
            b.publication_year,
            GROUP_CONCAT(DISTINCT a.name) AS authors
        FROM authors_fts fts
        JOIN authors a ON a.id = fts.rowid
        JOIN book_authors ba ON ba.author_id = a.id
        JOIN books b ON b.id = ba.book_id
        WHERE authors_fts MATCH ?
        GROUP BY b.id
        ORDER BY b.title
    """
    fts_term = f'"{term}"*'
    return conn.execute(query, (fts_term,)).fetchall()


def search_by_year(conn: sqlite3.Connection, year: int) -> list[sqlite3.Row]:
    """
    Search books by publication year (exact match).

    Returns books with their authors.
    """
    query = """
        SELECT
            b.id,
            b.isbn,
            b.title,
            b.publication_year,
            GROUP_CONCAT(DISTINCT a.name) AS authors
        FROM books b
        LEFT JOIN book_authors ba ON ba.book_id = b.id
        LEFT JOIN authors a ON a.id = ba.author_id
        WHERE b.publication_year = ?
        GROUP BY b.id
        ORDER BY b.title
    """
    return conn.execute(query, (year,)).fetchall()


def browse_by_title(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Return all books ordered alphabetically by title."""
    query = """
        SELECT
            b.id,
            b.isbn,
            b.title,
            b.publication_year,
            GROUP_CONCAT(DISTINCT a.name) AS authors
        FROM books b
        LEFT JOIN book_authors ba ON ba.book_id = b.id
        LEFT JOIN authors a ON a.id = ba.author_id
        GROUP BY b.id
        ORDER BY b.title COLLATE NOCASE
    """
    return conn.execute(query).fetchall()


def browse_by_year(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Return all books ordered by publication year."""
    query = """
        SELECT
            b.id,
            b.isbn,
            b.title,
            b.publication_year,
            GROUP_CONCAT(DISTINCT a.name) AS authors
        FROM books b
        LEFT JOIN book_authors ba ON ba.book_id = b.id
        LEFT JOIN authors a ON a.id = ba.author_id
        GROUP BY b.id
        ORDER BY b.publication_year, b.title COLLATE NOCASE
    """
    return conn.execute(query).fetchall()


def browse_by_author(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Return all books ordered alphabetically by author name."""
    query = """
        SELECT
            b.id,
            b.isbn,
            b.title,
            b.publication_year,
            GROUP_CONCAT(DISTINCT a.name) AS authors,
            MIN(a.name) AS sort_author
        FROM books b
        LEFT JOIN book_authors ba ON ba.book_id = b.id
        LEFT JOIN authors a ON a.id = ba.author_id
        GROUP BY b.id
        ORDER BY sort_author COLLATE NOCASE, b.title COLLATE NOCASE
    """
    return conn.execute(query).fetchall()


def browse(db_path: Path | None, field: str) -> str:
    """
    Browse all books ordered by the specified field.

    Args:
        db_path: Path to database, or None for default.
        field: One of 'title', 'author', 'year'.

    Returns:
        Formatted string of results.
    """
    conn = get_connection(db_path)
    try:
        if field == "title":
            results = browse_by_title(conn)
        elif field == "author":
            results = browse_by_author(conn)
        elif field == "year":
            results = browse_by_year(conn)
        else:
            return f"Unknown browse field: {field}"

        return format_results(results)
    finally:
        conn.close()


def format_results(results: list[sqlite3.Row]) -> str:
    """Format search results for terminal display."""
    if not results:
        return "No books found."

    lines = []
    lines.append(f"Found {len(results)} book(s):\n")
    lines.append("-" * 60)

    for row in results:
        lines.append(f"Title:   {row['title']}")
        lines.append(f"Author:  {row['authors'] or 'Unknown'}")
        lines.append(f"Year:    {row['publication_year'] or 'Unknown'}")
        lines.append(f"ISBN:    {row['isbn']}")
        lines.append("-" * 60)

    return "\n".join(lines)


def search(db_path: Path | None, field: str, term: str) -> str:
    """
    Main search entry point.

    Args:
        db_path: Path to database, or None for default.
        field: One of 'title', 'author', 'year'.
        term: The search term.

    Returns:
        Formatted string of results.
    """
    conn = get_connection(db_path)
    try:
        if field == "title":
            results = search_by_title(conn, term)
        elif field == "author":
            results = search_by_author(conn, term)
        elif field == "year":
            results = search_by_year(conn, int(term))
        else:
            return f"Unknown search field: {field}"

        return format_results(results)
    finally:
        conn.close()


def main():
    """Command-line interface for search."""
    import argparse

    parser = argparse.ArgumentParser(description="Search the library database.")
    parser.add_argument(
        "field",
        choices=["title", "author", "year"],
        help="Field to search by"
    )
    parser.add_argument(
        "term",
        help="Search term"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help=f"Path to database (default: {DEFAULT_DB_PATH})"
    )

    args = parser.parse_args()
    print(search(args.db, args.field, args.term))


if __name__ == "__main__":
    main()
