# CLI Guard SQL
import  CLI_SQL.CLI_Guard_SQL as sqlite

# Import curses for Terminal User Interface and navigation
# https://docs.python.org/3/library/curses.html
import curses
import curses.panel

from typing import Any
import time



# Create custom Curses colour pairs
def customColours() -> dict[str, int]:

    curses.start_color()

    # Define color pairs
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    WHITE_BACKGROUND_ATTR = curses.color_pair(1)

    # Define dictionary for passing custom colour pairs through functions
    custom_colours: dict[str, int] = {
        "WHITE_BACKGROUND": WHITE_BACKGROUND_ATTR,
    }

    return custom_colours



# Create Curses Windows and Panels
def createWindows(stdscr: curses.window) -> dict[str, Any]:

    custom_colours = customColours()

    # Clear screen
    stdscr.clear()

    # Get the screen dimensions
    height, width = stdscr.getmaxyx()

    # Check against minimum size
    if height < 21 or width < 65:
        # End curses before printing
        curses.endwin()
        print(f"Terminal too small ({width}x{height}). Minimum required ~65x20.")
        exit(1)

    # Set Window sizes dynamically to avoid  overlapping
    answer_height = 5
    message_height = 6

    menu_start_y = answer_height # Y position where menu starts
    menu_height = height - (menu_start_y + message_height)
    menu_width = 21

    content_start_y = answer_height # Y position where content starts, doubled handling for clarity
    content_start_x = menu_width # X position where content starts
    content_height = height - (answer_height + message_height)
    content_width  = width - content_start_x

    message_start_y = answer_height + content_height

    # Define windows with calculated positions and sizes
    answer_window = curses.newwin(answer_height, width, 0, 0)
    answer_window.box()

    menu_window = curses.newwin(menu_height, menu_width, menu_start_y, 0)
    menu_window.box()

    content_window = curses.newwin(content_height, content_width, content_start_y, content_start_x)
    content_window.box()

    message_window = curses.newwin(message_height, width, message_start_y, 0)
    message_window.bkgd(' ', custom_colours["WHITE_BACKGROUND"])

    # Create panels
    login_window = curses.newwin(content_height, width, answer_height, 0)
    login_panel = curses.panel.new_panel(login_window)
    login_panel.hide()

    # User Menu is 6 lines in height with a start Y position of 13
    user_window = curses.newwin(6, menu_width, 13, menu_width)
    user_panel = curses.panel.new_panel(user_window)
    user_panel.hide()

    # Migration Menu is 5 lines in height with a start Y position of 14
    migration_window = curses.newwin(5, menu_width, 14, menu_width)
    migration_panel = curses.panel.new_panel(migration_window)
    migration_panel.hide()

    # User Menu is 6 lines in height with a start Y position of 15
    settings_window = curses.newwin(6, 21, 15, 21)
    settings_panel = curses.panel.new_panel(settings_window)
    settings_panel.hide()

    popup_height = 12
    popup_width = 60
    # Ensure popup fits
    if popup_height >= height or popup_width >= width:
         curses.endwin()
         print(f"Terminal too small ({width}x{height}) for popup ({popup_width}x{popup_height}).")
         exit(1)
    # Center popup relative to height and width
    popup_start_y = max(0, (height // 2) - (popup_height // 2))
    popup_start_x = max(0, (width // 2) - (popup_width // 2))
    popup_window = curses.newwin(popup_height, popup_width, popup_start_y, popup_start_x)
    popup_panel = curses.panel.new_panel(popup_window)
    popup_panel.hide()

    # Define dictionary key-value pairs for passing Windows and Panels through functions
    windows: dict[str, Any] = {
        "stdscr":               stdscr,
        "message_window":          message_window,
        "login_window":         login_window,
        "login_panel":          login_panel,
        "answer_window":       answer_window,
        "menu_window":          menu_window,
        "content_window":       content_window,
        "user_window":          user_window,
        "user_panel":           user_panel,
        "migration_window":     migration_window,
        "migration_panel":      migration_panel,
        "settings_window":      settings_window,
        "settings_panel":       settings_panel,
        "popup_window":         popup_window,
        "popup_panel":          popup_panel
    }

    return windows



def signIn(windows: dict[str, Any]) -> None:    

    # Define windows
    login_window = windows["login_window"]
    login_panel = windows["login_panel"]

    # Show login_panel and update content of login_window
    login_panel.show()
    login_window.addstr(1, 3, "Select a User to Sign In")

    # Mark window for update
    login_window.noutrefresh()
    # Initial draw
    curses.doupdate()

    time.sleep(10) #  Testing

    # Hide the login_panel and enter the main interaction loop
    login_panel.hide()
    mainMenu(windows)



def mainMenu(windows: dict[str, Any]) -> None:

    #  Define windows
    answer_window = windows["answer_window"]
    menu_window = windows["menu_window"]
    content_window = windows["content_window"]
    message_window = windows["message_window"]

    # Draw initial state created by createWindows
    # Mark all initially visible windows again
    answer_window.noutrefresh()
    menu_window.noutrefresh()
    content_window.noutrefresh()
    message_window.noutrefresh()

    # Draw everything marked
    curses.doupdate()


    user = None # CHANGE THIS / FIX THIS
    menu_window.addstr(1, 2, "MAIN MENU")
    # Display Current User information in the fourth and third last available row of the Terminal
    menu_window.addstr(menu_window.getmaxyx()[0] - 4, 2, "Current User:")
    menu_window.addstr(menu_window.getmaxyx()[0] - 3, 2, f"{user}")

    # menu_window.noutrefresh() # Mark for update
    # curses.doupdate() # Update marked windows

    # Menu options
    options = ["Passwords", "User Management", "Migrate Database", "Settings", "Sign Out", "Quit"]
    current_row = 0

    # Map menu options to functions
    functions = {
        0: passwordManagement,
        1: userManagement,
        2: migrateDatabase,
        3: settingsManagement,
        4: signOut,
        5: quitMenu
    }

    while True:

        # Display the menu
        for i, option in enumerate(options):
            if i == current_row:
                # Highlight the selected option
                menu_window.attron(curses.A_REVERSE)
                menu_window.addstr(i + 3, 2, option)
                menu_window.attroff(curses.A_REVERSE)
            else:
                menu_window.addstr(i + 3, 2, option)

        # Disable cursor and enable keypad input
        curses.curs_set(0)
        menu_window.keypad(True)
        # Get user input
        key = menu_window.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) - 1:
            current_row += 1
        elif key == 10:  # ASCII value for Enter key
            # Call the function corresponding to the selected option and pass the dictionary of windows
            functions[current_row](windows)



def passwordManagement(windows: dict[str, Any]) -> None:
    content_window = windows["content_window"]
    content_window.erase()
    content_window.box()
    content_window.addstr(3, 3, "User selected Passwords")
    content_window.noutrefresh() # Mark for update
    curses.doupdate() # Update marked windows



def userManagement(windows: dict[str, Any]) -> None:
    content_window = windows["content_window"]
    content_window.erase()
    content_window.box()
    content_window.addstr(3, 3, "User selected User Management")
    content_window.noutrefresh() # Mark for update
    curses.doupdate() # Update marked windows



def migrateDatabase(windows: dict[str, Any]) -> None:
    content_window = windows["content_window"]
    content_window.erase()
    content_window.box()
    content_window.addstr(3, 3, "User selected Migrate Database")
    content_window.noutrefresh() # Mark for update
    curses.doupdate() # Update marked windows



def settingsManagement(windows: dict[str, Any]) -> None:
    content_window = windows["content_window"]
    content_window.erase()
    content_window.box()
    content_window.addstr(3, 3, "User selected Settings")
    content_window.noutrefresh() # Mark for update
    curses.doupdate() # Update marked windows



def signOut(windows: dict[str, Any]) -> None:
    content_window = windows["content_window"]
    content_window.erase()
    content_window.box()
    content_window.addstr(3, 3, "User selected Sign Out")
    content_window.noutrefresh() # Mark for update
    curses.doupdate() # Update marked windows



def quitMenu(windows: dict[str, Any]) -> None:
    content_window = windows["content_window"]
    content_window.erase()
    content_window.box()
    content_window.addstr(3, 3, "Quitting...")
    content_window.noutrefresh() # Mark for update
    curses.doupdate() # Update marked windows
    time.sleep(0.5)
    exit()



def launch(stdscr: curses.window):

    curses.curs_set(0)      # Hide cursor
    stdscr.keypad(True)     # Enable special keys for stdscr (catches keys if no other window does)
    curses.noecho()         # Don't automatically echo typed keys
    curses.cbreak()         # React to keys instantly, without waiting for Enter

    # Create windows and initialise dictionary to pass through functions
    # createWindows should NOT call doupdate
    windows = createWindows(stdscr)

    # launch into Sign In panel
    signIn(windows)



if __name__ == "__main__":
    curses.wrapper(launch)