"""
Database initialization script.

Creates the library SQLite database from the schema file.
Warns and asks for confirmation if the database already exists.
"""

import sqlite3
import sys
from pathlib import Path


# Default database location (can be overridden via command line)
DEFAULT_DB_PATH = Path(__file__).parent / "library.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def confirm_overwrite(db_path: Path) -> bool:
    """Ask user to confirm overwriting an existing database."""
    print(f"WARNING: Database already exists at {db_path}")
    print("Continuing will DELETE all existing library data.")
    print()
    response = input("Type 'yes' to confirm deletion and recreate: ")
    return response.strip().lower() == "yes"


def create_database(db_path: Path, schema_path: Path) -> None:
    """Create the database from the schema file."""
    print(f"Creating database at {db_path}")

    # Read the schema
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    # Connect and execute schema
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(schema_sql)
        conn.commit()
        print("Database created successfully.")
    finally:
        conn.close()


def init_db(db_path: Path | None = None, force: bool = False) -> bool:
    """
    Initialize the database.

    Args:
        db_path: Path to the database file. Uses default if not specified.
        force: If True, skip confirmation prompt when overwriting.

    Returns:
        True if database was created, False if user cancelled.
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH

    # Check schema exists
    if not SCHEMA_PATH.exists():
        print(f"Error: Schema file not found at {SCHEMA_PATH}")
        return False

    # Handle existing database
    if db_path.exists():
        if not force:
            if not confirm_overwrite(db_path):
                print("Cancelled. Database unchanged.")
                return False
        db_path.unlink()
        print(f"Removed existing database.")

    # Create fresh database
    create_database(db_path, SCHEMA_PATH)
    return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Initialize the library database."
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Path to database file (default: {DEFAULT_DB_PATH})"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation when overwriting existing database"
    )

    args = parser.parse_args()

    success = init_db(db_path=args.db, force=args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
