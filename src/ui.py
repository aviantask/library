"""
Library terminal user interface.

A green-screen TUI for searching the library catalog.
"""

import curses
from pathlib import Path

from search import search, browse


DB_PATH = Path(__file__).parent / "db" / "library.db"

# Menu options
SEARCH_OPTIONS = [
    ("search_title", "Search by Title"),
    ("search_author", "Search by Author"),
    ("search_year", "Search by Year"),
]

BROWSE_OPTIONS = [
    ("browse_title", "Browse by Title"),
    ("browse_author", "Browse by Author"),
    ("browse_year", "Browse by Year"),
]


class LibraryUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.last_search = None  # (field, term) tuple
        self.setup_colors()

    def setup_colors(self):
        """Initialize green-on-black color scheme."""
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Highlighted
        self.stdscr.bkgd(' ', curses.color_pair(1))

    def draw_header(self):
        """Draw the header bar."""
        height, width = self.stdscr.getmaxyx()
        title = " LIBRARY CATALOG "
        self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.addstr(0, 0, " " * width)
        self.stdscr.addstr(0, (width - len(title)) // 2, title)
        self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

    def draw_footer(self, message=""):
        """Draw the footer bar with optional message."""
        height, width = self.stdscr.getmaxyx()
        footer = message or " [Q]uit "
        self.stdscr.attron(curses.color_pair(2))
        self.stdscr.addstr(height - 1, 0, " " * (width - 1))
        self.stdscr.addstr(height - 1, 0, footer[:width - 1])
        self.stdscr.attroff(curses.color_pair(2))

    def show_main_menu(self):
        """Display main menu and return selected option."""
        selected = 0
        menu_items = []

        # Add repeat last search option if available
        if self.last_search:
            field, term = self.last_search
            menu_items.append(("repeat", f"Repeat: {field} = '{term}'"))

        # Add separators and sections
        menu_items.append(("_search_header", "── Search ──"))
        menu_items.extend(SEARCH_OPTIONS)
        menu_items.append(("_browse_header", "── Browse ──"))
        menu_items.extend(BROWSE_OPTIONS)

        menu_items.append(("quit", "Quit"))

        # Find selectable items (skip headers)
        selectable = [i for i, (key, _) in enumerate(menu_items) if not key.startswith("_")]
        selected = selectable[0] if selectable else 0

        while True:
            self.stdscr.clear()
            self.draw_header()
            self.draw_footer(" [↑/↓] Navigate  [Enter] Select  [Q] Quit ")

            height, width = self.stdscr.getmaxyx()
            start_y = 3

            # Draw menu
            for i, (key, label) in enumerate(menu_items):
                y = start_y + i
                if y >= height - 2:
                    break

                if key.startswith("_"):
                    # Section header
                    self.stdscr.addstr(y, 2, label, curses.A_DIM)
                elif i == selected:
                    self.stdscr.attron(curses.color_pair(2))
                    self.stdscr.addstr(y, 2, f" {label} ")
                    self.stdscr.attroff(curses.color_pair(2))
                else:
                    self.stdscr.addstr(y, 4, label)

            self.stdscr.refresh()

            ch = self.stdscr.getch()
            if ch == curses.KEY_UP:
                # Find previous selectable item
                curr_idx = selectable.index(selected) if selected in selectable else 0
                if curr_idx > 0:
                    selected = selectable[curr_idx - 1]
            elif ch == curses.KEY_DOWN:
                # Find next selectable item
                curr_idx = selectable.index(selected) if selected in selectable else -1
                if curr_idx < len(selectable) - 1:
                    selected = selectable[curr_idx + 1]
            elif ch in (curses.KEY_ENTER, 10, 13):
                return menu_items[selected][0]
            elif ch in (ord('q'), ord('Q')):
                return "quit"

    def get_search_input(self, field: str) -> str | None:
        """Prompt user for search term. Returns None if cancelled."""
        self.stdscr.clear()
        self.draw_header()
        self.draw_footer(" [Enter] Search  [Esc] Cancel ")

        height, width = self.stdscr.getmaxyx()
        prompt = f"Enter {field}: "
        self.stdscr.addstr(3, 2, prompt)
        self.stdscr.refresh()

        # Enable cursor and echo for input
        curses.curs_set(1)
        curses.echo()

        # Create input window
        input_win = curses.newwin(1, width - len(prompt) - 4, 3, len(prompt) + 2)
        input_win.bkgd(' ', curses.color_pair(1))

        term = ""
        while True:
            input_win.clear()
            input_win.addstr(0, 0, term)
            input_win.refresh()

            ch = self.stdscr.getch()
            if ch == 27:  # Escape
                curses.curs_set(0)
                curses.noecho()
                return None
            elif ch in (curses.KEY_ENTER, 10, 13):
                curses.curs_set(0)
                curses.noecho()
                return term if term.strip() else None
            elif ch in (curses.KEY_BACKSPACE, 127, 8):
                term = term[:-1]
            elif 32 <= ch <= 126:  # Printable ASCII
                term += chr(ch)

    def show_results(self, results_text: str):
        """Display search results with scrolling."""
        lines = results_text.split('\n')
        scroll_pos = 0

        while True:
            self.stdscr.clear()
            self.draw_header()
            self.draw_footer(" [↑/↓] Scroll  [u/d] Half-page  [Enter/Q] Back ")

            height, width = self.stdscr.getmaxyx()
            visible_lines = height - 3  # Account for header and footer

            # Draw visible portion of results
            for i, line in enumerate(lines[scroll_pos:scroll_pos + visible_lines]):
                y = 2 + i
                if y >= height - 1:
                    break
                # Truncate long lines
                display_line = line[:width - 1] if len(line) >= width else line
                try:
                    self.stdscr.addstr(y, 0, display_line)
                except curses.error:
                    pass  # Ignore if we can't write (edge of screen)

            # Show scroll indicator
            if len(lines) > visible_lines:
                indicator = f" [{scroll_pos + 1}-{min(scroll_pos + visible_lines, len(lines))}/{len(lines)}] "
                self.stdscr.addstr(0, self.stdscr.getmaxyx()[1] - len(indicator) - 1, indicator,
                                   curses.color_pair(2) | curses.A_BOLD)

            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key == curses.KEY_UP and scroll_pos > 0:
                scroll_pos -= 1
            elif key == curses.KEY_DOWN and scroll_pos < len(lines) - visible_lines:
                scroll_pos += 1
            elif key == curses.KEY_PPAGE:  # Page Up
                scroll_pos = max(0, scroll_pos - visible_lines)
            elif key == curses.KEY_NPAGE:  # Page Down
                scroll_pos = min(len(lines) - visible_lines, scroll_pos + visible_lines)
            elif key == ord('u'):  # Half-page up
                scroll_pos = max(0, scroll_pos - visible_lines // 2)
            elif key == ord('d'):  # Half-page down
                scroll_pos = min(len(lines) - visible_lines, scroll_pos + visible_lines // 2)
            elif key in (curses.KEY_ENTER, 10, 13, ord('q'), ord('Q')):
                return

    def do_search(self, field: str, term: str):
        """Execute search and display results."""
        # Cache this search
        self.last_search = (field, term)

        # Show loading message
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 2, "Searching...")
        self.stdscr.refresh()

        # Execute search
        results_text = search(DB_PATH, field, term)
        self.show_results(results_text)

    def do_browse(self, field: str):
        """Execute browse and display results."""
        # Show loading message
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 2, "Loading...")
        self.stdscr.refresh()

        # Execute browse
        results_text = browse(DB_PATH, field)
        self.show_results(results_text)

    def run(self):
        """Main UI loop."""
        curses.curs_set(0)  # Hide cursor

        while True:
            choice = self.show_main_menu()

            if choice == "quit":
                break
            elif choice == "repeat":
                if self.last_search:
                    field, term = self.last_search
                    self.do_search(field, term)
            elif choice.startswith("search_"):
                field = choice.replace("search_", "")
                term = self.get_search_input(field)
                if term:
                    self.do_search(field, term)
            elif choice.startswith("browse_"):
                field = choice.replace("browse_", "")
                self.do_browse(field)


def main(stdscr):
    """Entry point for curses wrapper."""
    ui = LibraryUI(stdscr)
    ui.run()


if __name__ == "__main__":
    curses.wrapper(main)
