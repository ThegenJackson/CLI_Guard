# CLI Guard SQL
import  CLI_SQL.CLI_Guard_SQL as sqlite

#CLI Guard Business Logic
import CLI_Guard

# Input validation
import validation

# Import curses for Terminal User Interface and navigation
# https://docs.python.org/3/library/curses.html
import curses
import curses.panel

import bcrypt

from typing import Any, Optional
import time

from logger import log



# Create custom Curses colour pairs
def customColours() -> dict[str, int]:

    curses.start_color()

    # Define color pairs
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    WHITE_BACKGROUND_ATTR: int = curses.color_pair(1)

    # Define dictionary for passing custom colour pairs through functions
    custom_colours: dict[str, int] = {
        "WHITE_BACKGROUND": WHITE_BACKGROUND_ATTR,
    }

    return custom_colours



# Create Curses Windows and Panels
def createWindows(stdscr: curses.window) -> dict[str, Any]:

    custom_colours: dict[str, int] = customColours()

    # Clear screen
    stdscr.clear()

    # Get the screen dimensions
    height: int = stdscr.getmaxyx()[0]
    width: int = stdscr.getmaxyx()[1]

    # Check against minimum size
    if height < 21 or width < 65:
        # End curses before printing
        curses.endwin()
        print(f"Terminal too small ({width}x{height}). Minimum required ~65x20.")
        exit(1)

    # Set Window sizes dynamically to avoid  overlapping
    answer_height: int = 5
    message_height: int = 5

    menu_start_y: int = answer_height # Y position where menu starts
    menu_height: int = height - (menu_start_y + message_height)
    menu_width: int = 21

    content_start_y: int = answer_height # Y position where content starts, doubled handling for clarity
    content_start_x:int  = menu_width # X position where content starts
    content_height: int = height - (answer_height + message_height)
    content_width: int  = width - content_start_x

    message_start_y: int = answer_height + content_height

    # Define windows with calculated positions and sizes
    answer_window: curses.window  = curses.newwin(answer_height, width, 0, 0)
    answer_window.box()

    menu_window: curses.window = curses.newwin(menu_height, menu_width, menu_start_y, 0)
    menu_window.box()

    content_window: curses.window = curses.newwin(content_height, content_width, content_start_y, content_start_x)
    content_window.box()

    message_window: curses.window = curses.newwin(message_height, width, message_start_y, 0)
    message_window.bkgd(' ', custom_colours["WHITE_BACKGROUND"])

    # Create panels
    login_window: curses.window = curses.newwin(content_height, width, answer_height, 0)
    login_panel: curses.panel.Panel = curses.panel.new_panel(login_window)
    login_panel.hide()

    # User Menu is 6 lines in height with a start Y position of 13
    user_window: curses.window = curses.newwin(6, menu_width, 13, menu_width)
    user_panel: curses.panel.Panel = curses.panel.new_panel(user_window)
    user_panel.hide()

    # Migration Menu is 5 lines in height with a start Y position of 14
    migration_window: curses.window = curses.newwin(5, menu_width, 14, menu_width)
    migration_panel: curses.panel.Panel = curses.panel.new_panel(migration_window)
    migration_panel.hide()

    # User Menu is 6 lines in height with a start Y position of 15
    settings_window: curses.window = curses.newwin(6, 21, 15, 21)
    settings_panel: curses.panel.Panel = curses.panel.new_panel(settings_window)
    settings_panel.hide()

    popup_height: int = 12
    popup_width: int = 60
    # Ensure popup fits
    if popup_height >= height or popup_width >= width:
         curses.endwin()
         print(f"Terminal too small ({width}x{height}) for popup ({popup_width}x{popup_height}).")
         exit(1)
    # Center popup relative to height and width
    popup_start_y: int = max(0, (height // 2) - (popup_height // 2))
    popup_start_x: int = max(0, (width // 2) - (popup_width // 2))
    popup_window: curses.window = curses.newwin(popup_height, popup_width, popup_start_y, popup_start_x)
    popup_panel: curses.panel.Panel = curses.panel.new_panel(popup_window)
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
        "popup_panel":          popup_panel,
        "stdscr":               stdscr
    }

    return windows



def signIn(windows: dict[str, Any], user=None) -> None:    

# WINDOWS
    # Define windows
    login_window: curses.window = windows["login_window"]
    login_panel: curses.panel.Panel  = windows["login_panel"]

    # Show login_panel and update content of login_window
    login_panel.show()
    login_window.box()
    login_window.addstr(0, 3, "| Select a User to Sign In |")
    
    # Mark window for update
    login_window.noutrefresh()
    # Initial draw
    curses.doupdate()

# LOGIC
    login_options: dict[str, Any] = {
    "Create new user":          createUser,
    "Exit":                     quitMenu
    }

    # Get Users
    users_list: list[str] = CLI_Guard.getUsers()
    # Sort users_list alphabetically
    users_list.sort()

    # Initialize selected value
    selected: int = 0
    selectable_items: int = len(users_list) + len(login_options) - 1

    # Main input loop for Sign In
    while True:

        # Display the data rows with scrolling
        for i, user_data in enumerate(users_list):
            if i == selected:
                login_window.attron(curses.A_REVERSE)
                login_window.addstr(i + 2, 3, user_data[0])
                login_window.attroff(curses.A_REVERSE)
            else:
                login_window.addstr(i + 2, 3, user_data[0])

        # Display options with highlighted state based on selected
        for i, option in enumerate(login_options, start=len(users_list)):
            if  i == selected:
                login_window.attron(curses.A_REVERSE)
                login_window.addstr(i + 3, 3, option)
                login_window.attroff(curses.A_REVERSE)
            else:
                login_window.addstr(i + 3, 3, option)

        login_window.refresh()

        # Enable Curses keypad in the login_window context
        login_window.keypad(True)
        # Get user input
        key: int = login_window.getch()

        # Scroll down
        if key == curses.KEY_DOWN and selected < selectable_items:
                selected += 1

        # Scroll up
        elif key == curses.KEY_UP and selected > 0:
                selected -= 1

        elif key == 10:  # ASCII value for Enter key
            if selected <= selectable_items - len(login_options):
                # Clear and redraw login_window
                login_window.erase()
                login_window.refresh() 
                login_panel.hide()

                # Pass windows and selected User to mainMenu
                authSignIn(windows, on_cancel=signIn, user=users_list[selected][0])

                # Break the loop after exiting
                break
            
            elif selected > selectable_items - len(login_options):
                # Convert the login_options Dictionary to a List containing only the Dictionary Keys
                # Convert the current_index to the correct index of the List by subtracting the length of users_list
                # Pass the windows Dictionary, createUser requires it and Exit uses the quitMenu Key for compability
                login_options[list(login_options.keys())[selected - len(users_list)]](windows, on_cancel=signIn)

                # Break the loop after exiting
                break



def authSignIn(windows: dict[str, Any], on_cancel, user: str) -> None:

# WINDOWS
    # Define windows
    login_window: curses.window = windows["login_window"]
    login_panel: curses.panel.Panel  = windows["login_panel"]
    message_window: curses.window = windows["message_window"]

    # Check if user is locked before allowing login
    if sqlite.isUserLocked(user):
        # Show locked message
        message_window.erase()
        message_window.addstr(2, 2, f"Account {user} is locked until tomorrow. Please try again later.")
        message_window.noutrefresh()
        curses.doupdate()
        time.sleep(3)

        # Clear message and return to sign in
        message_window.erase()
        message_window.noutrefresh()
        curses.doupdate()
        signIn(windows)
        return

    # Show login_panel and update content of login_window
    login_panel.show()
    login_window.box()
    login_window.addstr(0, 3, f"| Enter password for {user} |")

    # Mark window for update
    login_window.noutrefresh()
    # Initial draw
    curses.doupdate()

# LOGIC
    # Define input field as a list to assist in logic later despite list containing a single value
    # This method copies approach from createUser and createPassword to achieve forms in Python Curses
    auth_fields: list[str] = ["Password:"]
    auth_inputs: list[str] = ["" for _ in auth_fields]

    # Options
    auth_options: list[str] = ["Enter", "Cancel"]

    # initialise selected value
    selected: int = 0

    # Initialise attempted_password and attempts counter
    attempted_password: str = ""
    attempts: int = 0

    while True:

        # Draw fields and inputs
        for i, field in enumerate(auth_fields):
            login_window.addstr(2 + i, 2, field)
            login_window.addstr(2 + i, 20, auth_inputs[i])
            # Highlight inputs if selected
            if selected == i:
                login_window.addstr(2 + i, 2, field, curses.A_REVERSE)

        # Draw options
        for i, option in enumerate(auth_options):
            login_window.addstr(4, 2 + i * 10, f"{option:^10}")
            # Highlight active option
            if selected == len(auth_fields) + i:
                login_window.addstr(4, 2 + i * 10, f"{option:^10}", curses.A_REVERSE)

        login_window.refresh()

        # Enable Curses keypad in the login_window context
        login_window.keypad(True)
        # Get user input
        key: int = login_window.getch()

        # Scroll down
        if key == curses.KEY_DOWN and selected < len(auth_options):
            selected += 1

        # Return to Form inputs
        elif key == curses.KEY_UP:
            selected = 0

        # Navigate Right between auth_options
        elif key == curses.KEY_RIGHT and selected < len(auth_options):
            selected += 1

        # Navigate Left between auth_options
        elif key == curses.KEY_LEFT and 0 < selected <= len(auth_options):
            selected -= 1

        # Typing in the active field and tracking attempted_password
        elif selected == 0 and 32 <= key <= 126:
            attempted_password += chr(key)
            auth_inputs[selected] += "*"

        # Handle backspace (covering multiple cases) to modify attempted_password and inputted value
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if selected == 0 and auth_inputs[selected]:
                # Shorten the attempted_password
                attempted_password = attempted_password[:-1]
                # Shorten the inputted value
                auth_inputs[selected] = auth_inputs[selected][:-1]
                # Replace the value with the shortened input value
                login_window.addstr(2 + selected, 20 + len(auth_inputs[selected]), " ")

        elif key == 10 and selected < len(auth_options):  # ASCII value for Enter key, Cancel is not selected
            # Check if password was entered
            if not attempted_password:
                message_window.erase()
                message_window.addstr(2, 2, "Please enter a password")
                message_window.noutrefresh()
                curses.doupdate()
                time.sleep(2)
                message_window.erase()
                message_window.noutrefresh()
                curses.doupdate()
                continue

            # Authenticate user
            if CLI_Guard.authUser(user, attempted_password):
                # Authentication successful - start session
                CLI_Guard.startSession(user, attempted_password)

                # Clear login window and hide panel
                login_window.erase()
                login_window.refresh()
                login_panel.hide()

                # Go to main menu
                mainMenu(windows, user)
                break
            else:
                # Authentication failed - increment attempts
                attempts += 1

                if attempts >= 3:
                    # Lock the user account
                    sqlite.lockUser(user)

                    # Show lockout message
                    message_window.erase()
                    message_window.addstr(2, 2, f"Incorrect password entered 3 times. Account locked until tomorrow.")
                    message_window.noutrefresh()
                    curses.doupdate()
                    time.sleep(3)

                    # Clear and hide
                    login_window.erase()
                    login_window.refresh()
                    login_panel.hide()
                    message_window.erase()
                    message_window.noutrefresh()
                    curses.doupdate()

                    # Return to sign in
                    signIn(windows)
                    break
                else:
                    # Show error message with remaining attempts
                    remaining = 3 - attempts
                    message_window.erase()
                    message_window.addstr(2, 2, f"Incorrect password. {remaining} attempt(s) remaining.")
                    message_window.noutrefresh()
                    curses.doupdate()
                    time.sleep(2)

                    # Clear attempted password and reset input
                    attempted_password = ""
                    auth_inputs[0] = ""

                    # Clear message
                    message_window.erase()
                    message_window.noutrefresh()

                    # Redraw login window
                    login_window.erase()
                    login_window.box()
                    login_window.addstr(0, 3, f"| Enter password for {user} |")
                    login_window.noutrefresh()
                    curses.doupdate()

        elif key == 10 and selected == len(auth_options):  # Cancel selected
            # Erase current screen
            login_window.erase()
            login_window.border(0)
            login_window.refresh()
            login_panel.hide()

            # Return to Sign In
            signIn(windows)

            # Break the loop after exiting
            break



def mainMenu(windows: dict[str, Any], user: str) -> None:

# WINDOWS
    #  Define windows
    answer_window: curses.window = windows["answer_window"]
    menu_window: curses.window = windows["menu_window"]
    content_window: curses.window = windows["content_window"]
    message_window: curses.window = windows["message_window"]

    menu_window.addstr(1, 2, "MAIN MENU")
    # Display Current User information in the fourth and third last available row of the Terminal
    menu_window.addstr(menu_window.getmaxyx()[0] - 4, 2, "Current User:")
    menu_window.addstr(menu_window.getmaxyx()[0] - 3, 2, f"{user}")

    # Draw initial state created by createWindows
    # Mark all initially visible windows again
    answer_window.noutrefresh()
    menu_window.noutrefresh()
    content_window.noutrefresh()
    message_window.noutrefresh()

    # Draw everything marked
    curses.doupdate()


# LOGIC
    # Menu options
    options: list[str] = ["Passwords", "User Management", "Migrate Database", "Settings", "Sign Out", "Quit"]
    selected: int = 0

    # Map menu options to functions
    functions: dict[int, Any] = {
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
            if i == selected:
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
        key: int = menu_window.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(options) - 1:
            selected += 1
        elif key == 10:  # ASCII value for Enter key
            # Only signOut and quitMenu should exit the menu
            # Other functions should return to the menu after completing
            if selected == 4:  # Sign Out
                functions[selected](windows)
                break  # Exit menu after signing out
            elif selected == 5:  # Quit
                functions[selected](windows)
                break  # Exit menu after quitting (though quitMenu calls exit())
            else:
                # Call other functions but stay in menu
                functions[selected](windows)
                # Redraw the menu after function returns
                menu_window.clear()
                menu_window.box()
                menu_window.addstr(1, 2, "MAIN MENU")
                menu_window.addstr(menu_window.getmaxyx()[0] - 4, 2, "Current User:")
                menu_window.addstr(menu_window.getmaxyx()[0] - 3, 2, f"{user}")
                menu_window.noutrefresh()
                curses.doupdate()



def createPassword(windows: dict[str, Any]) -> Optional[list[str]]:
    """
    Create a new password entry with popup form

    Args:
        windows: Dictionary of curses windows and panels

    Returns:
        List of inputs [category, account, username, password] if Create clicked
        None if Cancel clicked
    """
    popup_window: curses.window = windows["popup_window"]
    popup_panel: curses.panel.Panel = windows["popup_panel"]
    menu_window: curses.window = windows["menu_window"]
    content_window: curses.window = windows["content_window"]

    # Show popup
    popup_panel.show()

    # Form fields
    fields: list[str] = ["Category:", "Account:", "Username:", "Password:"]
    inputs: list[str] = ["" for _ in fields]

    # Password generation options (placeholders)
    options: list[str] = ["Scramble Password", "Generate Random", "Generate Passphrase"]

    # Buttons
    buttons: list[str] = ["Create", "Cancel"]

    # Navigation state
    current_field: int = 0
    current_option: int = 0
    current_button: int = 0
    in_buttons: bool = False
    in_options: bool = False

    popup_window.keypad(True)
    running: bool = True

    while running:
        popup_window.erase()
        popup_window.box()
        popup_window.addstr(0, 2, "| Create New Password |")

        # Draw fields and inputs
        for i, field in enumerate(fields):
            popup_window.addstr(2 + i, 2, field)

            # Mask password field
            if i == 3:  # Password field
                popup_window.addstr(2 + i, 20, "*" * len(inputs[i]))
            else:
                popup_window.addstr(2 + i, 20, inputs[i])

            # Highlight active field
            if not in_buttons and not in_options and current_field == i:
                popup_window.addstr(2 + i, 2, field, curses.A_REVERSE)

        # Draw password generation options
        popup_window.addstr(7, 2, "Password Options:")
        for i, option in enumerate(options):
            x_pos = 2 + (i * 18)
            popup_window.addstr(8, x_pos, f"{option[:16]:^16}")

            if in_options and current_option == i:
                popup_window.addstr(8, x_pos, f"{option[:16]:^16}", curses.A_REVERSE)

        # Draw buttons
        for i, button in enumerate(buttons):
            x_pos = 20 + (i * 12)
            popup_window.addstr(10, x_pos, button)

            if in_buttons and current_button == i:
                popup_window.addstr(10, x_pos, button, curses.A_REVERSE)

        popup_window.noutrefresh()
        curses.doupdate()

        # Get user input
        key: int = popup_window.getch()

        # Navigation: DOWN
        if key == curses.KEY_DOWN:
            if not in_buttons and not in_options:
                current_field += 1
                if current_field >= len(fields):
                    in_options = True
                    current_field = len(fields) - 1
            elif in_options:
                in_options = False
                in_buttons = True

        # Navigation: UP
        elif key == curses.KEY_UP:
            if in_buttons:
                in_buttons = False
                in_options = True
            elif in_options:
                in_options = False
            else:
                current_field = max(0, current_field - 1)

        # Navigation: LEFT/RIGHT
        elif key == curses.KEY_LEFT:
            if in_options:
                current_option = (current_option - 1) % len(options)
            elif in_buttons:
                current_button = (current_button - 1) % len(buttons)

        elif key == curses.KEY_RIGHT:
            if in_options:
                current_option = (current_option + 1) % len(options)
            elif in_buttons:
                current_button = (current_button + 1) % len(buttons)

        # Typing in field
        elif not in_buttons and not in_options and 32 <= key <= 126:
            inputs[current_field] += chr(key)

        # Backspace
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if not in_buttons and not in_options and inputs[current_field]:
                inputs[current_field] = inputs[current_field][:-1]

        # Enter key
        elif key == 10:
            if in_buttons:
                if current_button == 1:  # Cancel
                    popup_panel.hide()
                    # Force complete redraw of menu and content windows
                    curses.panel.update_panels()
                    menu_window.touchwin()
                    menu_window.refresh()
                    content_window.touchwin()
                    content_window.refresh()
                    return None
                elif current_button == 0:  # Create
                    # Validate all fields are filled
                    if not all(inputs):
                        popup_window.addstr(0, 2, "| All fields required! |", curses.A_BOLD)
                        popup_window.noutrefresh()
                        curses.doupdate()
                        time.sleep(1)
                        continue

                    # Validate each field
                    category_valid, category_error = validation.validate_text_field(inputs[0], "Category", max_len=50)
                    if not category_valid:
                        popup_window.addstr(0, 2, f"| {category_error} |", curses.A_BOLD)
                        popup_window.noutrefresh()
                        curses.doupdate()
                        time.sleep(2)
                        continue

                    account_valid, account_error = validation.validate_text_field(inputs[1], "Account", max_len=100)
                    if not account_valid:
                        popup_window.addstr(0, 2, f"| {account_error} |", curses.A_BOLD)
                        popup_window.noutrefresh()
                        curses.doupdate()
                        time.sleep(2)
                        continue

                    username_valid, username_error = validation.validate_text_field(inputs[2], "Username", max_len=100)
                    if not username_valid:
                        popup_window.addstr(0, 2, f"| {username_error} |", curses.A_BOLD)
                        popup_window.noutrefresh()
                        curses.doupdate()
                        time.sleep(2)
                        continue

                    password_valid, password_error = validation.validate_text_field(inputs[3], "Password", min_len=1, max_len=500)
                    if not password_valid:
                        popup_window.addstr(0, 2, f"| {password_error} |", curses.A_BOLD)
                        popup_window.noutrefresh()
                        curses.doupdate()
                        time.sleep(2)
                        continue

                    # All validations passed
                    popup_panel.hide()
                    # Force complete redraw of menu and content windows
                    curses.panel.update_panels()
                    menu_window.touchwin()
                    menu_window.refresh()
                    content_window.touchwin()
                    content_window.refresh()
                    return inputs
            elif in_options:
                # Password generation options (placeholders for now)
                if current_option == 0:
                    inputs[3] = "ScrambledPass123!"
                elif current_option == 1:
                    inputs[3] = "RandomPass789$"
                elif current_option == 2:
                    inputs[3] = "correct-horse-battery-staple"
            else:
                # ENTER pressed on a form field - move to next field (like DOWN arrow)
                if not in_buttons and not in_options:
                    current_field += 1
                    if current_field >= len(fields):
                        in_options = True
                        current_field = len(fields) - 1

        # ESC key
        elif key == 27:
            popup_panel.hide()
            # Force complete redraw of menu and content windows
            curses.panel.update_panels()
            menu_window.touchwin()
            menu_window.refresh()
            content_window.touchwin()
            content_window.refresh()
            return None

    return None



def updatePassword(windows: dict[str, Any], existing_data: list) -> Optional[list[str]]:
    """
    Update an existing password entry with popup form

    Args:
        windows: Dictionary of curses windows and panels
        existing_data: Current password data [category, account, username, encrypted_password]

    Returns:
        List of updated inputs [category, account, username, password] if Update clicked
        None if Cancel clicked
    """
    popup_window: curses.window = windows["popup_window"]
    popup_panel: curses.panel.Panel = windows["popup_panel"]
    menu_window: curses.window = windows["menu_window"]
    content_window: curses.window = windows["content_window"]

    # Show popup
    popup_panel.show()

    # Form fields
    fields: list[str] = ["Category:", "Account:", "Username:", "Password:"]

    # Pre-fill inputs with existing data
    # Decrypt the password for editing
    try:
        decrypted_password = CLI_Guard.decryptPassword(existing_data[3])
    except Exception:
        # If decryption fails, leave blank
        decrypted_password = ""

    inputs: list[str] = [existing_data[0], existing_data[1], existing_data[2], decrypted_password]

    # Password generation options (placeholders)
    options: list[str] = ["Scramble Password", "Generate Random", "Generate Passphrase"]

    # Buttons
    buttons: list[str] = ["Update", "Cancel"]

    # Navigation state
    current_field: int = 0
    current_option: int = 0
    current_button: int = 0
    in_buttons: bool = False
    in_options: bool = False

    popup_window.keypad(True)
    running: bool = True

    while running:
        popup_window.erase()
        popup_window.box()
        popup_window.addstr(0, 2, "| Update Password |")

        # Draw fields and inputs
        for i, field in enumerate(fields):
            popup_window.addstr(2 + i, 2, field)

            # Mask password field
            if i == 3:  # Password field
                popup_window.addstr(2 + i, 20, "*" * len(inputs[i]))
            else:
                popup_window.addstr(2 + i, 20, inputs[i])

            # Highlight active field
            if not in_buttons and not in_options and current_field == i:
                popup_window.addstr(2 + i, 2, field, curses.A_REVERSE)

        # Draw password generation options
        popup_window.addstr(7, 2, "Password Options:")
        for i, option in enumerate(options):
            x_pos = 2 + (i * 18)
            popup_window.addstr(8, x_pos, f"{option[:16]:^16}")

            if in_options and current_option == i:
                popup_window.addstr(8, x_pos, f"{option[:16]:^16}", curses.A_REVERSE)

        # Draw buttons
        for i, button in enumerate(buttons):
            x_pos = 20 + (i * 12)
            popup_window.addstr(10, x_pos, button)

            if in_buttons and current_button == i:
                popup_window.addstr(10, x_pos, button, curses.A_REVERSE)

        popup_window.noutrefresh()
        curses.doupdate()

        # Get user input
        key: int = popup_window.getch()

        # Navigation: DOWN
        if key == curses.KEY_DOWN:
            if not in_buttons and not in_options:
                current_field += 1
                if current_field >= len(fields):
                    in_options = True
                    current_field = len(fields) - 1
            elif in_options:
                in_options = False
                in_buttons = True

        # Navigation: UP
        elif key == curses.KEY_UP:
            if in_buttons:
                in_buttons = False
                in_options = True
            elif in_options:
                in_options = False
            else:
                current_field = max(0, current_field - 1)

        # Navigation: LEFT/RIGHT
        elif key == curses.KEY_LEFT:
            if in_options:
                current_option = (current_option - 1) % len(options)
            elif in_buttons:
                current_button = (current_button - 1) % len(buttons)

        elif key == curses.KEY_RIGHT:
            if in_options:
                current_option = (current_option + 1) % len(options)
            elif in_buttons:
                current_button = (current_button + 1) % len(buttons)

        # Typing in field
        elif not in_buttons and not in_options and 32 <= key <= 126:
            inputs[current_field] += chr(key)

        # Backspace
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if not in_buttons and not in_options and inputs[current_field]:
                inputs[current_field] = inputs[current_field][:-1]

        # Enter key
        elif key == 10:
            if in_buttons:
                if current_button == 1:  # Cancel
                    popup_panel.hide()
                    # Force complete redraw of menu and content windows
                    curses.panel.update_panels()
                    menu_window.touchwin()
                    menu_window.refresh()
                    content_window.touchwin()
                    content_window.refresh()
                    return None
                elif current_button == 0:  # Update
                    # Validate all fields are filled
                    if not all(inputs):
                        popup_window.addstr(0, 2, "| All fields required! |", curses.A_BOLD)
                        popup_window.noutrefresh()
                        curses.doupdate()
                        time.sleep(1)
                        continue

                    # Validate each field
                    category_valid, category_error = validation.validate_text_field(inputs[0], "Category", max_len=50)
                    if not category_valid:
                        popup_window.addstr(0, 2, f"| {category_error} |", curses.A_BOLD)
                        popup_window.noutrefresh()
                        curses.doupdate()
                        time.sleep(2)
                        continue

                    account_valid, account_error = validation.validate_text_field(inputs[1], "Account", max_len=100)
                    if not account_valid:
                        popup_window.addstr(0, 2, f"| {account_error} |", curses.A_BOLD)
                        popup_window.noutrefresh()
                        curses.doupdate()
                        time.sleep(2)
                        continue

                    username_valid, username_error = validation.validate_text_field(inputs[2], "Username", max_len=100)
                    if not username_valid:
                        popup_window.addstr(0, 2, f"| {username_error} |", curses.A_BOLD)
                        popup_window.noutrefresh()
                        curses.doupdate()
                        time.sleep(2)
                        continue

                    password_valid, password_error = validation.validate_text_field(inputs[3], "Password", min_len=1, max_len=500)
                    if not password_valid:
                        popup_window.addstr(0, 2, f"| {password_error} |", curses.A_BOLD)
                        popup_window.noutrefresh()
                        curses.doupdate()
                        time.sleep(2)
                        continue

                    # All validations passed
                    popup_panel.hide()
                    # Force complete redraw of menu and content windows
                    curses.panel.update_panels()
                    menu_window.touchwin()
                    menu_window.refresh()
                    content_window.touchwin()
                    content_window.refresh()
                    return inputs
            elif in_options:
                # Password generation options (placeholders for now)
                if current_option == 0:
                    inputs[3] = "ScrambledPass123!"
                elif current_option == 1:
                    inputs[3] = "RandomPass789$"
                elif current_option == 2:
                    inputs[3] = "correct-horse-battery-staple"
            else:
                # ENTER pressed on a form field - move to next field
                if not in_buttons and not in_options:
                    current_field += 1
                    if current_field >= len(fields):
                        in_options = True
                        current_field = len(fields) - 1

        # ESC key
        elif key == 27:
            popup_panel.hide()
            # Force complete redraw of menu and content windows
            curses.panel.update_panels()
            menu_window.touchwin()
            menu_window.refresh()
            content_window.touchwin()
            content_window.refresh()
            return None

    return None



def viewPasswordDetails(windows: dict[str, Any], password_data: list) -> Optional[str]:
    """
    View password details in a popup with Update/Delete options

    Args:
        windows: Dictionary of curses windows and panels
        password_data: Password record [user, category, account, username, encrypted_password, last_modified]

    Returns:
        "update" if user wants to update
        "delete" if user wants to delete
        None if cancelled
    """
    popup_window: curses.window = windows["popup_window"]
    popup_panel: curses.panel.Panel = windows["popup_panel"]
    menu_window: curses.window = windows["menu_window"]
    content_window: curses.window = windows["content_window"]

    # Show popup
    popup_panel.show()

    # Extract data
    category = password_data[1]
    account = password_data[2]
    username = password_data[3]
    encrypted_password = password_data[4]
    last_modified = password_data[5]

    # Decrypt password for display
    try:
        decrypted_password = CLI_Guard.decryptPassword(encrypted_password)
    except Exception:
        decrypted_password = "[Decryption failed]"

    # Action buttons
    actions: list[str] = ["Update (U)", "Delete (D)", "Close (ESC)"]
    selected_action: int = 2  # Default to Close

    popup_window.keypad(True)
    running: bool = True

    while running:
        popup_window.erase()
        popup_window.box()
        popup_window.addstr(0, 2, "| Password Details |")

        # Display password details
        popup_window.addstr(2, 2, f"Category:      {category}")
        popup_window.addstr(3, 2, f"Account:       {account}")
        popup_window.addstr(4, 2, f"Username:      {username}")
        popup_window.addstr(5, 2, f"Password:      {decrypted_password}")
        popup_window.addstr(6, 2, f"Last Modified: {last_modified}")

        # Draw action buttons
        popup_window.addstr(8, 2, "Actions:")
        for i, action in enumerate(actions):
            y_pos = 9
            x_pos = 4 + (i * 16)
            if selected_action == i:
                popup_window.addstr(y_pos, x_pos, action, curses.A_REVERSE)
            else:
                popup_window.addstr(y_pos, x_pos, action)

        popup_window.noutrefresh()
        curses.doupdate()

        # Get user input
        key: int = popup_window.getch()

        # Navigation: LEFT/RIGHT
        if key == curses.KEY_LEFT:
            selected_action = (selected_action - 1) % len(actions)
        elif key == curses.KEY_RIGHT:
            selected_action = (selected_action + 1) % len(actions)

        # ENTER key
        elif key == 10:
            if selected_action == 0:  # Update
                popup_panel.hide()
                # Force complete redraw of menu and content windows
                curses.panel.update_panels()
                menu_window.touchwin()
                menu_window.refresh()
                content_window.touchwin()
                content_window.refresh()
                return "update"
            elif selected_action == 1:  # Delete
                popup_panel.hide()
                # Force complete redraw of menu and content windows
                curses.panel.update_panels()
                menu_window.touchwin()
                menu_window.refresh()
                content_window.touchwin()
                content_window.refresh()
                return "delete"
            else:  # Close
                popup_panel.hide()
                # Force complete redraw of menu and content windows
                curses.panel.update_panels()
                menu_window.touchwin()
                menu_window.refresh()
                content_window.touchwin()
                content_window.refresh()
                return None

        # Keyboard shortcuts
        elif key in (ord('u'), ord('U')):  # Update
            popup_panel.hide()
            menu_window.noutrefresh()
            content_window.erase()
            content_window.box()
            content_window.noutrefresh()
            curses.doupdate()
            return "update"
        elif key in (ord('d'), ord('D')):  # Delete
            popup_panel.hide()
            menu_window.noutrefresh()
            content_window.erase()
            content_window.box()
            content_window.noutrefresh()
            curses.doupdate()
            return "delete"

        # ESC key
        elif key == 27:
            popup_panel.hide()
            # Refresh windows to hide popup
            menu_window.noutrefresh()
            content_window.erase()
            content_window.box()
            content_window.noutrefresh()
            curses.doupdate()
            return None

    return None



def searchPasswords(windows: dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    """
    Search passwords popup interface

    Args:
        windows: Dictionary of curses windows and panels

    Returns:
        Tuple of (column, search_term) if Search clicked
        Tuple of (None, None) if Cancel clicked
    """
    popup_window: curses.window = windows["popup_window"]
    popup_panel: curses.panel.Panel = windows["popup_panel"]
    menu_window: curses.window = windows["menu_window"]
    content_window: curses.window = windows["content_window"]

    # Show popup
    popup_panel.show()

    # Column options for search
    column_options: list[str] = ["Category", "Account", "Username"]
    buttons: list[str] = ["Search", "Cancel"]

    # State
    selected_column: int = 0
    selected_button: int = 0
    search_term: str = ""
    in_buttons: bool = False
    in_text_field: bool = False
    column_selected: bool = False

    popup_window.keypad(True)
    running: bool = True

    while running:
        popup_window.erase()
        popup_window.box()
        popup_window.addstr(0, 2, "| Search Passwords |")

        # Draw column selection title
        popup_window.addstr(2, 2, "Search by:")

        # Draw column options
        for i, column in enumerate(column_options):
            y_pos = 3 + i
            if not column_selected and selected_column == i:
                popup_window.addstr(y_pos, 4, f"[{column}]", curses.A_REVERSE)
            elif column_selected and selected_column == i:
                popup_window.addstr(y_pos, 4, f"[{column}]", curses.A_BOLD)
            else:
                popup_window.addstr(y_pos, 4, f" {column} ")

        # Draw text field if column selected
        if column_selected:
            popup_window.addstr(7, 2, "Search term:")
            popup_window.addstr(8, 4, search_term)

            # Highlight text field if active
            if in_text_field:
                popup_window.addstr(7, 2, "Search term:", curses.A_REVERSE)

        # Draw buttons
        for i, button in enumerate(buttons):
            x_pos = 20 + (i * 12)
            if in_buttons and selected_button == i:
                popup_window.addstr(10, x_pos, button, curses.A_REVERSE)
            else:
                popup_window.addstr(10, x_pos, button)

        popup_window.noutrefresh()
        curses.doupdate()

        # Get user input
        key: int = popup_window.getch()

        # Navigation: UP/DOWN for column selection
        if not column_selected and key == curses.KEY_DOWN:
            selected_column = (selected_column + 1) % len(column_options)
        elif not column_selected and key == curses.KEY_UP:
            selected_column = (selected_column - 1) % len(column_options)

        # Navigation: DOWN from text field to buttons
        elif in_text_field and key == curses.KEY_DOWN:
            in_text_field = False
            in_buttons = True

        # Navigation: UP from buttons to text field
        elif in_buttons and key == curses.KEY_UP:
            in_buttons = False
            in_text_field = True

        # Navigation: LEFT/RIGHT for buttons
        elif in_buttons and key == curses.KEY_LEFT:
            selected_button = (selected_button - 1) % len(buttons)
        elif in_buttons and key == curses.KEY_RIGHT:
            selected_button = (selected_button + 1) % len(buttons)

        # Typing in text field
        elif in_text_field and 32 <= key <= 126:
            search_term += chr(key)

        # Backspace in text field
        elif in_text_field and key in (curses.KEY_BACKSPACE, 127, 8):
            if search_term:
                search_term = search_term[:-1]

        # ENTER key
        elif key == 10:
            if not column_selected:
                # Select column and move to text field
                column_selected = True
                in_text_field = True
            elif in_text_field:
                # Move to buttons
                in_text_field = False
                in_buttons = True
            elif in_buttons:
                if selected_button == 1:  # Cancel
                    popup_panel.hide()
                    # Force complete redraw of menu and content windows
                    curses.panel.update_panels()
                    menu_window.touchwin()
                    menu_window.refresh()
                    content_window.touchwin()
                    content_window.refresh()
                    return (None, None)
                elif selected_button == 0:  # Search
                    if not search_term:
                        popup_window.addstr(0, 2, "| Enter search term! |", curses.A_BOLD)
                        popup_window.noutrefresh()
                        curses.doupdate()
                        time.sleep(1)
                        continue

                    # Validate search term
                    search_valid, search_error = validation.validate_text_field(search_term, "Search term", max_len=100)
                    if not search_valid:
                        popup_window.addstr(0, 2, f"| {search_error} |", curses.A_BOLD)
                        popup_window.noutrefresh()
                        curses.doupdate()
                        time.sleep(2)
                        continue

                    # Validation passed
                    column_name = column_options[selected_column]
                    popup_panel.hide()
                    # Force complete redraw of menu and content windows
                    curses.panel.update_panels()
                    menu_window.touchwin()
                    menu_window.refresh()
                    content_window.touchwin()
                    content_window.refresh()
                    return (column_name, search_term)

        # ESC key
        elif key == 27:
            popup_panel.hide()
            # Force complete redraw of menu and content windows
            curses.panel.update_panels()
            menu_window.touchwin()
            menu_window.refresh()
            content_window.touchwin()
            content_window.refresh()
            return (None, None)

    return (None, None)



def sortPasswords(windows: dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    """
    Sort passwords popup interface

    Args:
        windows: Dictionary of curses windows and panels

    Returns:
        Tuple of (column, sort_order) if Sort clicked
        Tuple of (None, None) if Cancel clicked
    """
    popup_window: curses.window = windows["popup_window"]
    popup_panel: curses.panel.Panel = windows["popup_panel"]
    menu_window: curses.window = windows["menu_window"]
    content_window: curses.window = windows["content_window"]

    # Show popup
    popup_panel.show()

    # Column options for sorting
    column_options: list[str] = ["Category", "Account", "Username", "Last Modified"]
    sort_options: list[str] = ["Ascending", "Descending"]
    buttons: list[str] = ["Sort", "Cancel"]

    # State
    selected_column: int = 0
    selected_sort: int = 0
    selected_button: int = 0
    in_sort_options: bool = False
    in_buttons: bool = False
    column_selected: bool = False

    popup_window.keypad(True)
    running: bool = True

    while running:
        popup_window.erase()
        popup_window.box()
        popup_window.addstr(0, 2, "| Sort Passwords |")

        # Draw column selection
        popup_window.addstr(2, 2, "Sort by:")
        for i, column in enumerate(column_options):
            y_pos = 3 + i
            if not column_selected and selected_column == i:
                popup_window.addstr(y_pos, 4, f"[{column}]", curses.A_REVERSE)
            elif column_selected and selected_column == i:
                popup_window.addstr(y_pos, 4, f"[{column}]", curses.A_BOLD)
            else:
                popup_window.addstr(y_pos, 4, f" {column} ")

        # Draw sort order if column selected
        if column_selected:
            popup_window.addstr(8, 2, "Order:")
            for i, sort_opt in enumerate(sort_options):
                x_pos = 4 + (i * 15)
                if in_sort_options and selected_sort == i:
                    popup_window.addstr(9, x_pos, sort_opt, curses.A_REVERSE)
                elif not in_sort_options and not in_buttons:
                    # Auto-select first option when column is selected
                    if i == 0:
                        popup_window.addstr(9, x_pos, sort_opt, curses.A_BOLD)
                    else:
                        popup_window.addstr(9, x_pos, sort_opt)
                else:
                    popup_window.addstr(9, x_pos, sort_opt)

        # Draw buttons
        for i, button in enumerate(buttons):
            x_pos = 20 + (i * 12)
            if in_buttons and selected_button == i:
                popup_window.addstr(10, x_pos, button, curses.A_REVERSE)
            else:
                popup_window.addstr(10, x_pos, button)

        popup_window.noutrefresh()
        curses.doupdate()

        # Get user input
        key: int = popup_window.getch()

        # Navigation: UP/DOWN for column selection
        if not column_selected and key == curses.KEY_DOWN:
            selected_column = (selected_column + 1) % len(column_options)
        elif not column_selected and key == curses.KEY_UP:
            selected_column = (selected_column - 1) % len(column_options)

        # Navigation: DOWN from sort options to buttons
        elif in_sort_options and key == curses.KEY_DOWN:
            in_sort_options = False
            in_buttons = True

        # Navigation: UP from buttons to sort options
        elif in_buttons and key == curses.KEY_UP:
            in_buttons = False
            in_sort_options = True

        # Navigation: LEFT/RIGHT for sort options
        elif in_sort_options and key == curses.KEY_LEFT:
            selected_sort = (selected_sort - 1) % len(sort_options)
        elif in_sort_options and key == curses.KEY_RIGHT:
            selected_sort = (selected_sort + 1) % len(sort_options)

        # Navigation: LEFT/RIGHT for buttons
        elif in_buttons and key == curses.KEY_LEFT:
            selected_button = (selected_button - 1) % len(buttons)
        elif in_buttons and key == curses.KEY_RIGHT:
            selected_button = (selected_button + 1) % len(buttons)

        # ENTER key
        elif key == 10:
            if not column_selected:
                # Select column and move to sort options
                column_selected = True
                in_sort_options = True
            elif in_sort_options:
                # Move to buttons
                in_sort_options = False
                in_buttons = True
            elif in_buttons:
                if selected_button == 1:  # Cancel
                    popup_panel.hide()
                    # Force complete redraw of menu and content windows
                    curses.panel.update_panels()
                    menu_window.touchwin()
                    menu_window.refresh()
                    content_window.touchwin()
                    content_window.refresh()
                    return (None, None)
                elif selected_button == 0:  # Sort
                    column_name = column_options[selected_column]
                    sort_order = sort_options[selected_sort]
                    popup_panel.hide()
                    # Force complete redraw of menu and content windows
                    curses.panel.update_panels()
                    menu_window.touchwin()
                    menu_window.refresh()
                    content_window.touchwin()
                    content_window.refresh()
                    return (column_name, sort_order)

        # ESC key
        elif key == 27:
            popup_panel.hide()
            # Force complete redraw of menu and content windows
            curses.panel.update_panels()
            menu_window.touchwin()
            menu_window.refresh()
            content_window.touchwin()
            content_window.refresh()
            return (None, None)

    return (None, None)



def passwordManagement(windows: dict[str, Any]) -> None:
    """
    Password management interface with full CRUD operations

    Features:
    - View all passwords in scrollable table
    - Create new encrypted passwords
    - View decrypted password details
    - Search passwords by category, account, or username
    - Sort passwords by any column in ascending/descending order
    """
    content_window: curses.window = windows["content_window"]
    message_window: curses.window = windows["message_window"]
    popup_window: curses.window = windows["popup_window"]
    popup_panel: curses.panel.Panel = windows["popup_panel"]

    # Get current authenticated user from session
    user: Optional[str] = CLI_Guard.getSessionUser()
    if not user:
        message_window.erase()
        message_window.addstr(2, 2, "Error: No active session. Please sign in again.")
        message_window.noutrefresh()
        curses.doupdate()
        time.sleep(2)
        return

    # Options and headers (removed Update and Delete - they're in the password details popup)
    options: list[str] = ["Create Password (C)", "Search Passwords (S)", "Sort Passwords (O)"]
    headers: list[str] = ["Index", "Category", "Account", "Username", "Last Modified"]

    # Navigation state
    current_row: int = 0
    start_index: int = 0
    running: bool = True

    # Feature state (for search/sort)
    feature: Optional[str] = None
    category: Optional[str] = None
    sort_variable: Optional[str] = None
    search_term: Optional[str] = None

    while running:
        # Query passwords from database
        passwords_list: list[list] = []

        if feature is None:
            data = sqlite.queryData(user=user, table="passwords")
        elif feature == "Sort":
            data = sqlite.queryData(user=user, table="passwords", category=category, text=None, sort_by=sort_variable)
        elif feature == "Search":
            data = sqlite.queryData(user=user, table="passwords", category=category, text=search_term, sort_by=None)
        else:
            data = sqlite.queryData(user=user, table="passwords")

        # Build display list
        if data:
            for i, password in enumerate(data):
                # password tuple: [user, category, account, username, password, last_modified]
                passwords_list.append([i + 1, password[1], password[2], password[3], password[5]])

        # Calculate column width for table
        content_width: int = content_window.getmaxyx()[1] - 4
        column_width: int = (content_width - 10) // (len(headers) - 1)

        # Maximum visible rows in content window
        max_visible_rows: int = content_window.getmaxyx()[0] - 6

        # Clear and redraw content window
        content_window.erase()
        content_window.box()

        # Draw options at top
        for i, option in enumerate(options):
            if current_row == i:
                content_window.attron(curses.A_REVERSE)
            content_window.addstr(1, 2 + (column_width * i), option[:column_width-1])
            if current_row == i:
                content_window.attroff(curses.A_REVERSE)

        # Draw active filter status
        if feature == "Search" and category and search_term:
            content_window.addstr(2, 2, f"Filter: {category} contains '{search_term}' (ESC to clear)", curses.A_DIM)
        elif feature == "Sort" and category and sort_variable:
            content_window.addstr(2, 2, f"Sorted by: {category} ({sort_variable}) (ESC to clear)", curses.A_DIM)

        # Draw table headers
        content_window.addstr(3, 2, f"{headers[0]:<10}{headers[1]:<{column_width}}{headers[2]:<{column_width}}{headers[3]:<{column_width}}{headers[4]:<{column_width}}", curses.A_BOLD)

        # Ensure start_index is valid
        start_index = max(0, min(start_index, len(passwords_list) - max_visible_rows if len(passwords_list) > 0 else 0))

        # Get visible slice of passwords
        visible_passwords = passwords_list[start_index:start_index + max_visible_rows] if passwords_list else []

        # Draw password rows
        for i, row in enumerate(visible_passwords):
            row_index: int = i + 4
            is_selected: bool = (start_index + i) == (current_row - len(options))

            if is_selected:
                content_window.attron(curses.A_REVERSE)

            # Truncate long strings to fit column width
            display_row = [
                str(row[0])[:10],
                str(row[1])[:column_width-1],
                str(row[2])[:column_width-1],
                str(row[3])[:column_width-1],
                str(row[4])[:column_width-1]
            ]
            content_window.addstr(row_index, 2, f"{display_row[0]:<10}{display_row[1]:<{column_width}}{display_row[2]:<{column_width}}{display_row[3]:<{column_width}}{display_row[4]:<{column_width}}")

            if is_selected:
                content_window.attroff(curses.A_REVERSE)

        content_window.noutrefresh()
        curses.doupdate()

        # Get user input
        content_window.keypad(True)
        key: int = content_window.getch()

        # Navigation: Move from options to password list
        if 0 <= current_row <= (len(options) - 1) and key == curses.KEY_DOWN:
            current_row = len(options)

        # Navigation: Move from password list back to options
        elif current_row == len(options) and key == curses.KEY_UP:
            current_row = 0

        # Navigation: Between options (LEFT/RIGHT)
        elif 0 <= current_row <= (len(options) - 2) and key == curses.KEY_RIGHT:
            current_row += 1
        elif 1 <= current_row <= (len(options) - 1) and key == curses.KEY_LEFT:
            current_row -= 1

        # Navigation: Wrap around at end of list
        elif current_row == (len(passwords_list) + len(options) - 1) and key == curses.KEY_DOWN:
            current_row = len(options)
            start_index = 0

        # Navigation: Scroll down through passwords
        elif key == curses.KEY_DOWN:
            if current_row < (len(passwords_list) + len(options) - 1):
                current_row += 1
                if (current_row - len(options)) >= (start_index + max_visible_rows):
                    start_index += 1

        # Navigation: Scroll up through passwords
        elif key == curses.KEY_UP:
            if current_row > 0:
                current_row -= 1
                if (current_row - len(options)) < start_index:
                    start_index -= 1

        # Enter key: Select option or password
        elif key == 10:
            if current_row == 0:  # Create Password
                # Call createPassword function
                inputs = createPassword(windows)
                if inputs:
                    # Extract fields
                    category_input = inputs[0]
                    account = inputs[1]
                    username_input = inputs[2]
                    plaintext_password = inputs[3]

                    # Encrypt password
                    encrypted_password = CLI_Guard.encryptPassword(plaintext_password)

                    # Save to database
                    sqlite.insertData(user, category_input, account, username_input, encrypted_password)
                    log("TUI", f"Password created for account '{account}' by user '{user}'")

                    # Show success message
                    message_window.erase()
                    message_window.addstr(2, 2, f"Password for {account} created successfully")
                    message_window.noutrefresh()
                    curses.doupdate()
                    time.sleep(1)
                    message_window.erase()
                    message_window.noutrefresh()
                    # Refresh password list - loop continues to requery and redraw

            elif current_row == 1:  # Search Passwords
                # Call searchPasswords function
                search_column, search_text = searchPasswords(windows)
                if search_column and search_text:
                    log("TUI", f"Search: {search_column} contains '{search_text}'")
                    # Set search parameters
                    feature = "Search"
                    category = search_column
                    search_term = search_text
                    # Reset current_row to first password
                    current_row = len(options)
                    start_index = 0
                    # Refresh password list - continue to requery and redraw
                    # Don't use break here as it exits the entire function!

            elif current_row == 2:  # Sort Passwords
                # Call sortPasswords function
                sort_column, sort_order = sortPasswords(windows)
                if sort_column and sort_order:
                    log("TUI", f"Sort: {sort_column} {sort_order}")
                    # Set sort parameters
                    feature = "Sort"
                    category = sort_column
                    sort_variable = sort_order
                    # Reset current_row to first password
                    current_row = len(options)
                    start_index = 0
                    # Refresh password list - continue to requery and redraw
                    # Don't use break here as it exits the entire function!

            else:  # Password row selected
                if passwords_list and (current_row - len(options)) < len(passwords_list):
                    selected_record = passwords_list[current_row - len(options)]

                    # Get original data row to access all password data
                    data_index = selected_record[0] - 1
                    original_record = data[data_index]

                    # Show password details popup
                    action = viewPasswordDetails(windows, original_record)

                    if action == "update":
                        # Prepare existing data for update form
                        existing_data = [
                            original_record[1],  # category
                            original_record[2],  # account
                            original_record[3],  # username
                            original_record[4]   # encrypted password
                        ]

                        # Call updatePassword with existing data
                        updated_inputs = updatePassword(windows, existing_data)
                        if updated_inputs:
                            new_category = updated_inputs[0]
                            new_account = updated_inputs[1]
                            new_username = updated_inputs[2]
                            new_plaintext_password = updated_inputs[3]

                            # Encrypt new password
                            new_encrypted_password = CLI_Guard.encryptPassword(new_plaintext_password)

                            # Update in database
                            sqlite.updateData(user, new_encrypted_password, new_account, new_username, original_record[4])
                            log("TUI", f"Password updated for account '{new_account}' by user '{user}'")

                            message_window.erase()
                            message_window.addstr(2, 2, f"Password for {new_account} updated successfully")
                            message_window.noutrefresh()
                            curses.doupdate()
                            time.sleep(1)
                            message_window.erase()
                            message_window.noutrefresh()
                            # Loop continues to requery and redraw

                    elif action == "delete":
                        # Show confirmation dialog
                        confirm_msg = f"Delete password for {original_record[2]}? (Y/N)"
                        message_window.erase()
                        message_window.addstr(2, 2, confirm_msg, curses.A_BOLD)
                        message_window.noutrefresh()
                        curses.doupdate()

                        # Wait for confirmation
                        message_window.keypad(True)
                        confirm_key = message_window.getch()

                        if confirm_key in (ord('y'), ord('Y')):
                            # Delete from database
                            sqlite.deleteData(
                                user,
                                original_record[2],  # account
                                original_record[3],  # username
                                original_record[4]   # encrypted password
                            )
                            log("TUI", f"Password deleted for account '{original_record[2]}' by user '{user}'")

                            message_window.erase()
                            message_window.addstr(2, 2, f"Password for {original_record[2]} deleted successfully")
                            message_window.noutrefresh()
                            curses.doupdate()
                            time.sleep(1)
                            message_window.erase()
                            message_window.noutrefresh()
                            # Loop continues to requery and redraw
                        else:
                            # Cancelled - just clear message
                            message_window.erase()
                            message_window.noutrefresh()

        # ESC key: Clear filter or return to main menu
        elif key == 27:
            # If there's an active filter, clear it
            if feature in ["Search", "Sort"]:
                feature = None
                category = None
                sort_variable = None
                search_term = None
                current_row = 0
                start_index = 0
                # Show cleared message
                message_window.erase()
                message_window.addstr(2, 2, "Filter cleared - showing all passwords")
                message_window.noutrefresh()
                curses.doupdate()
                time.sleep(1)
                message_window.erase()
                message_window.noutrefresh()
                # Refresh list
                break
            else:
                # No active filter - exit to main menu
                content_window.erase()
                content_window.box()
                content_window.noutrefresh()
                message_window.erase()
                message_window.noutrefresh()
                curses.doupdate()
                running = False
                break

        # Keyboard shortcuts
        elif key in (ord('c'), ord('C')):  # Create Password
            inputs = createPassword(windows)
            if inputs:
                category_input = inputs[0]
                account = inputs[1]
                username_input = inputs[2]
                plaintext_password = inputs[3]
                encrypted_password = CLI_Guard.encryptPassword(plaintext_password)
                sqlite.insertData(user, category_input, account, username_input, encrypted_password)
                message_window.erase()
                message_window.addstr(2, 2, f"Password for {account} created successfully")
                message_window.noutrefresh()
                curses.doupdate()
                time.sleep(1)
                break



def userManagement(windows: dict[str, Any]) -> None:
    """
    User management interface (placeholder - to be implemented)

    This function will handle:
    - Creating new users
    - Updating user passwords
    - Deleting users
    """
    content_window: curses.window = windows["content_window"]
    message_window: curses.window = windows["message_window"]

    content_window.erase()
    content_window.box()
    content_window.addstr(3, 3, "User Management - Coming Soon")
    content_window.addstr(5, 3, "This feature is under development.")
    content_window.addstr(6, 3, "Press any key to return to Main Menu...")
    content_window.noutrefresh()

    message_window.erase()
    message_window.addstr(2, 2, "User Management - Under Development")
    message_window.noutrefresh()

    curses.doupdate()

    # Wait for user to press a key
    content_window.getch()

    # Clear windows before returning
    content_window.erase()
    content_window.box()
    content_window.noutrefresh()
    message_window.erase()
    message_window.noutrefresh()
    curses.doupdate()



def createUser(windows: dict[str, any], on_cancel, user=None) -> None:

# WINDOWS
    # Define windows
    popup_window: curses.window = windows["popup_window"]
    popup_panel: curses.panel.Panel  = windows["popup_panel"]

    # Show login_panel and update content of login_window
    popup_panel.show()
    popup_window.box()
    
    # Mark window for update
    popup_window.noutrefresh()
    # Initial draw
    curses.doupdate()

# LOGIC
    # Create a dictionary to hold the form data
    # The keys are the internal names of the fields
    # The values are the inputs, which start as empty strings
    create_user_fields: dict[str, str] = {
        "Username":         "",
        "Password":         ""
    }

    # Use an ordered list of the keys for display
    form_fields: list[str] = list(create_user_fields.keys())
    form_inputs: list[str] = ["" for _ in create_user_fields]

    # Top row options
    create_user_options: dict[str, Any] = {     # FIX THIS / CHANGE THIS TO ACTUAL FUNCTIONS   
        "Scramble Password":         goBack,
        "Generate Random":           goBack,
        "Generate Passphrase":       goBack
    }
    
    # Bottom row options
    create_user_options_extended: dict[str, Any] = {
        "Create":                   sqlite.insertUser,
        "Cancel":                   goBack
        }

    # initialise selected value
    selected: int = 0
    selectable_items: int = len(form_fields) + len(create_user_options) + len(create_user_options_extended) - 1


    while True:
        
        # Draw fields and inputs
        for i, field in enumerate(form_fields):
            popup_window.addstr(2 + i, 2, f"{field}:")
            popup_window.addstr(2 + i, 20, form_inputs[i])
            # Highlight inputs if selected
            if selected == i:
                popup_window.addstr(2 + i, 2, f"{field}:", curses.A_REVERSE)

        # Draw options
        for i, option in enumerate(create_user_options):
            popup_window.addstr(7, 2 + (i * 18), f"{option:^18}")
            # Highlight active option
            if selected == i + len(form_fields):
                popup_window.addstr(7, 2 + (i * 18), f"{option:^18}", curses.A_REVERSE)

        # Draw extended options
        for i, option in enumerate(create_user_options_extended):
            popup_window.addstr(9, 10 + (i * 18), f"{option:^18}")
            # Highlight active option
            if selected == i + len(form_fields) + len(create_user_options):
                popup_window.addstr(9, 10 + (i * 18), f"{option:^18}", curses.A_REVERSE)
        
        popup_window.refresh()

        # Enable Curses keypad in the login_window context
        popup_window.keypad(True)
        # Get user input
        key: int = popup_window.getch()

        # Scroll down
        if key == curses.KEY_DOWN and selected < selectable_items:
            if len(form_fields) - 1 < selected < len(form_fields) + len(create_user_options):
                selected = len(form_fields) + len(create_user_options)
            else: 
                selected += 1
    
        # Scroll up
        elif key == curses.KEY_UP and selected > 0:
            if len(form_fields) + len(create_user_options) - 1 < selected:
                selected = len(form_fields)
            else: 
                selected -= 1

        # Navigate Right between buttons
        elif key == curses.KEY_RIGHT and selected < selectable_items:
            selected += 1
        
        # Navigate Left between buttons
        elif key == curses.KEY_LEFT and selected <= selectable_items:
            selected -= 1

        # Typing in the active field
        elif 32 <= key <= 126 and selected < len(form_fields):
            create_user_fields[form_fields[selected]] += chr(key)

            if selected == len(form_fields) - 1:
                form_inputs[selected] += "*"
            else:
                form_inputs[selected] += chr(key)

        # Handle backspace (covering multiple cases)
        elif key in (curses.KEY_BACKSPACE, 127, 8) and selected < len(form_fields):
            form_inputs[selected] = form_inputs[selected][:-1]
            create_user_fields[form_fields[selected]] = form_inputs[selected][:-1]
            # Replace the value with the shortened input value
            popup_window.addstr(2 + selected, 20 + len(form_inputs[selected]), " ")

        elif key == 10:
            if selected == len(form_fields) + len(create_user_options):
                # Validate username
                new_user_username: str = create_user_fields["Username"]
                username_valid, username_error = validation.validate_username(new_user_username)
                if not username_valid:
                    popup_window.addstr(0, 2, f"| {username_error} |", curses.A_BOLD)
                    popup_window.noutrefresh()
                    curses.doupdate()
                    time.sleep(2)
                    popup_window.erase()
                    popup_window.box()
                    popup_window.noutrefresh()
                    curses.doupdate()
                    continue

                # Validate password (master password needs strong requirements)
                new_user_password: str = create_user_fields["Password"]
                password_valid, password_error = validation.validate_password(new_user_password)
                if not password_valid:
                    popup_window.addstr(0, 2, f"| {password_error} |", curses.A_BOLD)
                    popup_window.noutrefresh()
                    curses.doupdate()
                    time.sleep(2)
                    popup_window.erase()
                    popup_window.box()
                    popup_window.noutrefresh()
                    curses.doupdate()
                    continue

                # All validations passed - create user
                new_hashed_password: bytes = hashUser(password=new_user_password)
                sqlite.insertUser(user=new_user_username, password=new_hashed_password)

                stdscr: curses.window = windows["stdscr"]
                launch(stdscr)

                # Break the loop after exiting
                break

            if selected == selectable_items:
                popup_window.erase()
                popup_window.refresh()
                popup_panel.hide()

                on_cancel(windows, user)
                break



def hashUser(password: str) -> bytes:
    """
    Hash a password using bcrypt for storage

    Args:
        password: Plaintext password to hash

    Returns:
        Bcrypt hashed password as bytes
    """
    return CLI_Guard.hashPassword(password)



def migrateDatabase(windows: dict[str, Any]) -> None:
    """
    Database migration interface (placeholder - to be implemented)

    This function will handle:
    - Exporting database to file
    - Importing database from file
    """
    content_window: curses.window = windows["content_window"]
    message_window: curses.window = windows["message_window"]

    content_window.erase()
    content_window.box()
    content_window.addstr(3, 3, "Database Migration - Coming Soon")
    content_window.addstr(5, 3, "This feature is under development.")
    content_window.addstr(6, 3, "Press any key to return to Main Menu...")
    content_window.noutrefresh()

    message_window.erase()
    message_window.addstr(2, 2, "Database Migration - Under Development")
    message_window.noutrefresh()

    curses.doupdate()

    # Wait for user to press a key
    content_window.getch()

    # Clear windows before returning
    content_window.erase()
    content_window.box()
    content_window.noutrefresh()
    message_window.erase()
    message_window.noutrefresh()
    curses.doupdate()



def settingsManagement(windows: dict[str, Any]) -> None:
    """
    Settings management interface (placeholder - to be implemented)

    This function will handle:
    - Password generator settings
    - Application preferences
    - Security settings
    """
    content_window: curses.window = windows["content_window"]
    message_window: curses.window = windows["message_window"]

    content_window.erase()
    content_window.box()
    content_window.addstr(3, 3, "Settings - Coming Soon")
    content_window.addstr(5, 3, "This feature is under development.")
    content_window.addstr(6, 3, "Press any key to return to Main Menu...")
    content_window.noutrefresh()

    message_window.erase()
    message_window.addstr(2, 2, "Settings - Under Development")
    message_window.noutrefresh()

    curses.doupdate()

    # Wait for user to press a key
    content_window.getch()

    # Clear windows before returning
    content_window.erase()
    content_window.box()
    content_window.noutrefresh()
    message_window.erase()
    message_window.noutrefresh()
    curses.doupdate()



def signOut(windows: dict[str, Any]) -> None:
    """
    Sign out the current user and clear the session

    This ends the current session, clearing the encryption key from memory,
    then returns to the sign-in screen.
    """
    # End the session to clear encryption key from memory
    CLI_Guard.endSession()

    # Return to sign-in screen
    stdscr: curses.window = windows["stdscr"]
    launch(stdscr)



def quitMenu(windows: dict[str, Any], on_cancel=None) -> None:
    time.sleep(0.2)
    exit()



def goBack() ->  None:
    pass



def launch(stdscr: curses.window):

    curses.curs_set(0)      # Hide cursor
    stdscr.keypad(True)     # Enable special keys for stdscr (catches keys if no other window does)
    curses.noecho()         # Don't automatically echo typed keys
    curses.cbreak()         # React to keys instantly, without waiting for Enter

    # Create windows and initialise dictionary to pass through functions
    # createWindows should NOT call doupdate
    windows: dict[str, Any] = createWindows(stdscr)

    # launch into Sign In panel
    signIn(windows)



if __name__ == "__main__":
    curses.wrapper(launch)
