# Library System - Feature Checklist

## Core Components

### Ingestion Pipeline
- [x] Develop ingestion script that fetches books by ISBN
  - Parse ISBNs from input file
  - Lookup books via OpenLibrary API/scraping
  - Extract title, authors, publication date, DDC classification
  - Implement rate limiting
- [x] Insert ingested books into database

### Book Database
- [x] Design and implement database schema
  - Title, author(s), publication year
  - Support for storing additional metadata
- [ ] Setup database on shared network directory
- [x] Create database initialization scripts

### Search Functionality
- [x] Implement search by title
  - Include fuzzy search support
- [x] Implement search by author
  - Include fuzzy search support
- [x] Implement search by year
- [x] Create SQL query layer for search operations

### User Interface
- [x] Design and implement terminal-based UI (green-screen theme)
- [x] Implement guest user query interface
  - Display search results
  - Handle user input for searches
- [x] Browse ability
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
- [ ] Adjust due date when extension is granted (via application logic, outside DB)
- [ ] Display borrowing history and status in UI
