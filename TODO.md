# Library System - Feature Checklist

## Core Components

### Ingestion Pipeline
- [x] Develop ingestion script that fetches books by ISBN
  - Parse ISBNs from input file
  - Lookup books via OpenLibrary API/scraping
  - Extract title, authors, publication date, DDC classification
  - Implement rate limiting
- [ ] Insert ingested books into database

### Book Database
- [ ] Design and implement database schema
  - Title, author(s), publication year, topic
  - Support for storing additional metadata
- [ ] Setup database on shared network directory
- [ ] Create database initialization scripts

### Search Functionality
- [ ] Implement search by title
  - Include fuzzy search support
- [ ] Implement search by author
  - Include fuzzy search support
- [ ] Implement search by year
- [ ] Implement search by topic
  - Include fuzzy search support
- [ ] Create SQL query layer for search operations

### User Interface
- [ ] Design and implement terminal-based UI (green-screen theme)
- [ ] Implement guest user query interface
  - Display search results
  - Handle user input for searches
- [ ] Implement library admin user interface
  - Book checkout functionality
  - User account switching

### Borrowing System
- [ ] Implement book checkout/borrowing functionality
- [ ] Track borrowing information
  - Borrower name/ID
  - Borrow date
  - Return date
  - Borrow rate
  - Extension tracking
- [ ] Create borrowing records in database
- [ ] Implement return and extension workflows
- [ ] Display borrowing history and status in UI
