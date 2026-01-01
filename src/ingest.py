"""
Ingestion script for fetching book data from Open Library.

This script:
1. Reads ISBNs from a file (one per line)
2. Queries Open Library API for each ISBN
3. Extracts book metadata (title, author, description, etc.)
4. Outputs the data to JSON
"""

import json
import time
from pathlib import Path

import requests


# Rate limiting: wait this many seconds between requests
RATE_LIMIT_SECONDS = 1

OPEN_LIBRARY_API = "https://openlibrary.org"


def read_isbns(filepath: str) -> list[str]:
    """Read ISBNs from a file, one per line. Skip empty lines."""
    isbns = []
    with open(filepath, "r") as f:
        for line in f:
            isbn = line.strip()
            if isbn:
                isbn = isbn.replace('-', '')
                isbn = isbn.replace(' ', '')
                isbns.append(isbn)
    return isbns


def fetch_edition_data(session: requests.Session, isbn: str) -> dict | None:
    """Fetch edition data for an ISBN from Open Library."""
    url = f"{OPEN_LIBRARY_API}/isbn/{isbn}.json"
    response = session.get(url)

    if response.status_code == 404:
        return None
    response.raise_for_status()

    return response.json()


def fetch_work_data(session: requests.Session, work_key: str) -> dict | None:
    """Fetch work data from Open Library."""
    url = f"{OPEN_LIBRARY_API}{work_key}.json"
    response = session.get(url)

    if response.status_code == 404:
        return None
    response.raise_for_status()

    return response.json()


def fetch_author_data(session: requests.Session, author_key: str) -> dict | None:
    """Fetch author data from Open Library."""
    url = f"{OPEN_LIBRARY_API}{author_key}.json"
    response = session.get(url)

    if response.status_code == 404:
        return None
    response.raise_for_status()

    return response.json()


def extract_description(work_data: dict) -> str:
    """Extract description from work data."""
    desc = work_data.get("description")
    if desc is None:
        return ""
    if isinstance(desc, dict):
        return desc.get("value", "")
    return str(desc)


def extract_first_sentence(data: dict) -> str:
    """Extract first sentence from edition or work data."""
    first_sentence = data.get("first_sentence")
    if first_sentence is None:
        return ""
    if isinstance(first_sentence, dict):
        return first_sentence.get("value", "")
    return str(first_sentence)


def extract_subjects(work_data: dict) -> list[str]:
    """Extract subjects from work data."""
    subjects = work_data.get("subjects", [])
    return subjects if isinstance(subjects, list) else []


def fetch_book_by_isbn(session: requests.Session, isbn: str) -> dict | None:
    """
    Fetch book data for a given ISBN from Open Library.

    Returns a dict with book metadata, or None if not found.
    """
    print(f"Fetching data for ISBN: {isbn}")

    # Get edition data
    edition = fetch_edition_data(session, isbn)
    if not edition:
        print(f"  Not found in Open Library")
        return None

    title = edition.get("title", "")
    print(f"  Title: {title}")

    # Get work data for more metadata
    work_data = {}
    works = edition.get("works", [])
    if works:
        work_key = works[0].get("key")
        if work_key:
            time.sleep(RATE_LIMIT_SECONDS)
            work_data = fetch_work_data(session, work_key) or {}

    # Get author names
    authors = []
    author_keys = edition.get("authors", []) or work_data.get("authors", [])
    for author_ref in author_keys:
        author_key = author_ref.get("key") if isinstance(author_ref, dict) else None
        if author_key:
            time.sleep(RATE_LIMIT_SECONDS)
            author_data = fetch_author_data(session, author_key)
            if author_data:
                name = author_data.get("name", "")
                if name:
                    authors.append(name)

    print(f"  Author(s): {', '.join(authors)}")

    # Build the book data
    book_data = {
        "isbn": isbn,
        "title": title,
        "authors": authors,
        "publication_date": edition.get("publish_date", ""),
        "publishers": [p.get("name", p) if isinstance(p, dict) else p
                       for p in edition.get("publishers", [])],
        "description": extract_description(work_data),
        "subjects": extract_subjects(work_data),
        "open_library_key": edition.get("key"),
    }

    return book_data


def main():
    """Main entry point for the ingestion script."""
    isbn_file = Path(__file__).parent / "data" / "isbn.txt"
    output_file = Path(__file__).parent / "data" / "output.json"

    isbns = read_isbns(isbn_file)
    print(f"Found {len(isbns)} ISBNs to process")
    print()

    session = requests.Session()
    session.headers.update({
        "User-Agent": "LibraryIngestion/1.0 (Personal Library Project)"
    })

    results = []
    for isbn in isbns:
        try:
            book_data = fetch_book_by_isbn(session, isbn)
            if book_data:
                results.append(book_data)
        except Exception as e:
            print(f"  Error: {e}")
        print()
        time.sleep(RATE_LIMIT_SECONDS)

    # Write results to JSON
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Wrote {len(results)} books to {output_file}")


if __name__ == "__main__":
    main()
