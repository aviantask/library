-- Library Database Schema
-- SQLite with FTS5 for fuzzy search support

PRAGMA foreign_keys = ON;

-- =============================================================================
-- CORE TABLES
-- =============================================================================

-- Books: The central entity
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    publication_date TEXT,           -- Original date string from source
    publication_year INTEGER,        -- Extracted year for filtering/sorting
    description TEXT,
    open_library_key TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Authors
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Subjects (topics)
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Publishers
CREATE TABLE publishers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- =============================================================================
-- JUNCTION TABLES (many-to-many relationships)
-- =============================================================================

CREATE TABLE book_authors (
    book_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

CREATE TABLE book_subjects (
    book_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, subject_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE TABLE book_publishers (
    book_id INTEGER NOT NULL,
    publisher_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, publisher_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (publisher_id) REFERENCES publishers(id) ON DELETE CASCADE
);

-- =============================================================================
-- BORROWING SYSTEM
-- =============================================================================

CREATE TABLE borrowers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE borrows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    borrower_id INTEGER NOT NULL,
    borrow_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    extensions INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (borrower_id) REFERENCES borrowers(id)
);

-- =============================================================================
-- INDEXES for common query patterns
-- =============================================================================

CREATE INDEX idx_books_year ON books(publication_year);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_borrows_book ON borrows(book_id);
CREATE INDEX idx_borrows_borrower ON borrows(borrower_id);
CREATE INDEX idx_borrows_active ON borrows(book_id) WHERE return_date IS NULL;

-- =============================================================================
-- FTS5 VIRTUAL TABLES for fuzzy search
-- =============================================================================

-- Full-text search on book titles
CREATE VIRTUAL TABLE books_fts USING fts5(
    title,
    content='books',
    content_rowid='id'
);

-- Full-text search on author names
CREATE VIRTUAL TABLE authors_fts USING fts5(
    name,
    content='authors',
    content_rowid='id'
);

-- Full-text search on subject names
CREATE VIRTUAL TABLE subjects_fts USING fts5(
    name,
    content='subjects',
    content_rowid='id'
);

-- =============================================================================
-- TRIGGERS to keep FTS tables synchronized
-- =============================================================================

-- Books FTS triggers
CREATE TRIGGER books_fts_insert AFTER INSERT ON books BEGIN
    INSERT INTO books_fts(rowid, title) VALUES (new.id, new.title);
END;

CREATE TRIGGER books_fts_delete AFTER DELETE ON books BEGIN
    INSERT INTO books_fts(books_fts, rowid, title) VALUES('delete', old.id, old.title);
END;

CREATE TRIGGER books_fts_update AFTER UPDATE ON books BEGIN
    INSERT INTO books_fts(books_fts, rowid, title) VALUES('delete', old.id, old.title);
    INSERT INTO books_fts(rowid, title) VALUES (new.id, new.title);
END;

-- Authors FTS triggers
CREATE TRIGGER authors_fts_insert AFTER INSERT ON authors BEGIN
    INSERT INTO authors_fts(rowid, name) VALUES (new.id, new.name);
END;

CREATE TRIGGER authors_fts_delete AFTER DELETE ON authors BEGIN
    INSERT INTO authors_fts(authors_fts, rowid, name) VALUES('delete', old.id, old.name);
END;

CREATE TRIGGER authors_fts_update AFTER UPDATE ON authors BEGIN
    INSERT INTO authors_fts(authors_fts, rowid, name) VALUES('delete', old.id, old.name);
    INSERT INTO authors_fts(rowid, name) VALUES (new.id, new.name);
END;

-- Subjects FTS triggers
CREATE TRIGGER subjects_fts_insert AFTER INSERT ON subjects BEGIN
    INSERT INTO subjects_fts(rowid, name) VALUES (new.id, new.name);
END;

CREATE TRIGGER subjects_fts_delete AFTER DELETE ON subjects BEGIN
    INSERT INTO subjects_fts(subjects_fts, rowid, name) VALUES('delete', old.id, old.name);
END;

CREATE TRIGGER subjects_fts_update AFTER UPDATE ON subjects BEGIN
    INSERT INTO subjects_fts(subjects_fts, rowid, name) VALUES('delete', old.id, old.name);
    INSERT INTO subjects_fts(rowid, name) VALUES (new.id, new.name);
END;
