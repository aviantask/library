# Purpose
A local library system, with the following features:
* Ingest library books into the system via their ISBN
    * Ingested books are inserted into a database with (at least) title, author, publication year
* Search for books in the library
    * Search by title, author, or year
    * Fuzzy-search enabled
* Check books out
    * Books can be "borrowed", i.e. given to someone who takes them out of the home
    * Borrows are tracked - borrower, borrow rate, return date, extensions 

# Components
## Ingestion
### Book data
A separate pipeline exists for loading books into the library. 
A file is created with ISBNs, which a script will parse and work with. 
The ingestion script will perform a lookup on the ISBN using OpenLibrary API and extract the following:
* Title
* Author(s)
* Author information
* Publication date
* Classification, as per DDC/MDS

This info is scraped rather than found via API because I can't find APIs that offer all this info. 
The script rate limits itself to not overwhelm the OpenLibrary server. 

### Book databse
Canonical book data, as described above, is inserted into a database.
This database is basically the library. 
The database is stored on a shared network directory so it can be queried by the UI (another component). 

## UI
The UI lives on an old machine running Linux without a graphical display. 

## Queries
The UI loads into a `guest` user account that has the ability to query the library. 
The queries, e.g by author or year, issue SQL queries against the database and display the results. 
The entire UI is green-screen, because that's the vibe I'm after. 

## Borrowing
Guests need a `libraryadmin` user to check books out for them, i.e. to borrow them. 
The UI offers the option to switch to the library admin user, who enters the relevant details to check out the book. 

# Coding style
This is a python codebase, both the ingestion pipeline and the UI. 
There is are only two principles the codebase follows religiously:
1. Clarity of code above all else.
2. After clarify, simplicity above all else. 

Source files live in `./src`. The project uses a python venv so don't bother looking for source files at the project root, or alternatively you should exclude files in `./venv`.
Documentation is in README.md and `./docs`
Scripts are in `./scripts`.

