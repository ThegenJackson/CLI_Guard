# CLI Guard SQL
import  CLI_SQL.CLI_Guard_SQL as sqlite

# CLI Guard Business Logic
import CLI_Guard_Deprecated as CLI_Guard

# Import curses for Terminal User Interface and navigation
# https://docs.python.org/3/library/curses.html
import curses
import curses.panel

import time

# Define custom colours to extend curses predefined colours
# Convert RGB values (0-255) to curses scale (0-1000)
def customColours(r, g, b):
    return int(r / 255 * 1000), int(g / 255 * 1000), int(b / 255 * 1000)


def displayLogo(logo_window):
    curses.start_color()

    # Define custom colours with names
    custom_colours = {
        "blue_gradient_1": (0, 0, 255),
        "blue_gradient_2": (29, 80, 247),
        "blue_gradient_3": (43, 120, 242),
        "blue_gradient_4": (57, 160, 242),
        "blue_gradient_5": (72, 197, 243),
        "blue_gradient_6": (86, 236, 242)
    }

    # Initialize custom colours and colour pairs (use indices 100-109 to avoid conflicts)
    colour_pairs = {}
    for i, (name, (r, g, b)) in enumerate(custom_colours.items(), start=100):
        curses.init_color(i, *customColours(r, g, b))  # Define RGB in curses scale
        curses.init_pair(i - 99, i, curses.COLOR_BLACK)  # Create a colour pair
        colour_pairs[name] = i - 99

    # Multi-line logo with corresponding colour pair IDs
    logo_lines = [
        ("blue_gradient_1", " ██████╗ ██╗      ██╗     ██████╗  ██╗   ██╗  █████╗  ██████╗  ██████╗"),
        ("blue_gradient_2", "██╔════╝ ██║      ██║    ██╔════╝  ██║   ██║ ██╔══██╗ ██╔══██╗ ██╔══██╗"),
        ("blue_gradient_3", "██║      ██║      ██║    ██║  ███╗ ██║   ██║ ███████║ ██████╔╝ ██║  ██║"),
        ("blue_gradient_4", "██║      ██║      ██║    ██║   ██║ ██║   ██║ ██╔══██║ ██╔══██╗ ██║  ██║"),
        ("blue_gradient_5", "╚██████╗ ███████╗ ██║    ╚██████╔╝ ╚██████╔╝ ██║  ██║ ██║  ██║ ██████╔╝"),
        ("blue_gradient_6", " ╚═════╝ ╚══════╝ ╚═╝     ╚═════╝   ╚═════╝  ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═════╝")
    ]

    # Display the logo with gradient colours in the  logo_window
    for i, (colour_name, line) in enumerate(logo_lines):
        pair_id = colour_pairs[colour_name]
        logo_window.attron(curses.color_pair(pair_id))
        logo_window.addstr(i + 1, 6, line + "\n")
        logo_window.attroff(curses.color_pair(pair_id))



def createWindows(stdscr):

    # Clear screen
    stdscr.clear()

    # Get the screen dimensions
    height, width = stdscr.getmaxyx()

    # Create a main window
    main_win = curses.newwin(height, width, 0, 0)

    # Create sub windows within the main window
    logo_window = curses.newwin(8, width, 0, 0)

    message_window = curses.newwin(3, width, 7, 0)
    message_window.border(0)

    menu_window = curses.newwin(height - 10, 21, 10, 0)
    menu_window.border(0)

    user_menu = curses.newwin(6, 21, 13, 21)
    user_menu.border(0)
    user_menu_panel = curses.panel.new_panel(user_menu)
    user_menu_panel.hide()

    migration_menu = curses.newwin(5, 21, 14, 21)
    migration_menu.border(0)
    migration_menu_panel = curses.panel.new_panel(migration_menu)
    migration_menu_panel.hide()

    settings_menu = curses.newwin(6, 21, 15, 21)
    settings_menu.border(0)
    settings_menu_panel = curses.panel.new_panel(settings_menu)
    settings_menu_panel.hide()

    context_window = curses.newwin(height - 10, width - 21, 10, 21)
    context_window.border(0)

    popup_window = curses.newwin(12, 60, (height // 2) - 3, (width //2) - 30)
    popup_window.border(0)
    popup_window_panel = curses.panel.new_panel(popup_window)
    popup_window_panel.hide()

    # Print the Logo to logo_window
    displayLogo(logo_window)

    # Return all windows and panels for use by other functions
    return {
        'main_win': main_win,
        'logo_window': logo_window,
        'message_window': message_window,
        'menu_window': menu_window,
        'user_menu': user_menu,
        'user_menu_panel': user_menu_panel,
        'migration_menu': migration_menu,
        'migration_menu_panel': migration_menu_panel,
        'settings_menu': settings_menu,
        'settings_menu_panel': settings_menu_panel,
        'context_window': context_window,
        'popup_window': popup_window,
        'popup_window_panel': popup_window_panel,
        'stdscr': stdscr
    }



def signIn(windows):
    """User sign-in interface with authentication"""
    context_window = windows['context_window']
    message_window = windows['message_window']

    # Get list of users
    users_list = CLI_Guard.getUsers()

    if not users_list:
        message_window.erase()
        message_window.border(0)
        message_window.addstr(1, 2, "No users found. Create one in CLI first.")
        message_window.refresh()
        time.sleep(3)
        return None

    selected = 0

    while True:
        context_window.erase()
        context_window.border(0)
        context_window.addstr(1, 2, "Select user to sign in:", curses.A_BOLD)

        for i, user_data in enumerate(users_list):
            if i == selected:
                context_window.attron(curses.A_REVERSE)
            context_window.addstr(i + 3, 4, user_data[0])
            if i == selected:
                context_window.attroff(curses.A_REVERSE)

        quit_idx = len(users_list)
        if selected == quit_idx:
            context_window.attron(curses.A_REVERSE)
        context_window.addstr(quit_idx + 4, 4, "Quit")
        if selected == quit_idx:
            context_window.attroff(curses.A_REVERSE)

        context_window.refresh()

        key = context_window.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < quit_idx:
            selected += 1
        elif key == 10:  # Enter
            if selected == quit_idx:
                return None
            else:
                user = users_list[selected][0]
                if authenticateUser(windows, user):
                    return user
        elif key == 27:  # ESC
            return None



def authenticateUser(windows, user):
    """Authenticate user with password"""
    context_window = windows['context_window']
    message_window = windows['message_window']

    if sqlite.isUserLocked(user):
        message_window.erase()
        message_window.border(0)
        message_window.addstr(1, 2, f"Account {user} locked until tomorrow")
        message_window.refresh()
        time.sleep(3)
        return False

    attempts = 0
    while attempts < 3:
        context_window.erase()
        context_window.border(0)
        context_window.addstr(1, 2, f"Enter password for {user}:")
        context_window.addstr(3, 2, "Password: ")
        context_window.refresh()

        password = ""
        curses.echo(False)

        while True:
            key = context_window.getch()
            if key == 10:
                break
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                if password:
                    password = password[:-1]
                    context_window.addstr(3, 12 + len(password), " ")
            elif 32 <= key <= 126:
                password += chr(key)
                context_window.addstr(3, 12 + len(password) - 1, "*")
            elif key == 27:
                return False

        if CLI_Guard.authUser(user, password):
            CLI_Guard.startSession(user, password)
            return True
        else:
            attempts += 1
            if attempts >= 3:
                sqlite.lockUser(user)
                message_window.erase()
                message_window.border(0)
                message_window.addstr(1, 2, "Too many attempts. Account locked.")
                message_window.refresh()
                time.sleep(3)
                return False
            else:
                message_window.erase()
                message_window.border(0)
                message_window.addstr(1, 2, f"Incorrect. {3 - attempts} attempts left")
                message_window.refresh()
                time.sleep(2)

    return False



def mainMenu(menu_window, message_window, user_menu, user_menu_panel, migration_menu, migration_menu_panel, settings_menu, settings_menu_panel, popup_window, popup_window_panel,  context_window, user):

    def drawHeaders(context_window, headers, column_width):
        context_window.addstr(3, 2, f"{headers[0]:<10}{headers[1]:<{column_width}}{headers[2]:<{column_width}}{headers[3]:<{column_width}}{headers[4]:<{column_width}}", curses.A_BOLD)
        context_window.refresh()

    def passwordManagement(feature=None, category=None, sort_variable=None):
        options = ["Create Password", "Search Passwords", "Sort Passwords"]
        headers = ["Index", "Category", "Account", "Username", "Last Modified"]

        # Main loop controller
        running = True

        while running:

            # Create empty list to insert data into
            passwords_list = []

            if feature == None:
                # Query the passwords table and insert all into passwords_list ordered by account name
                data = sqlite.queryData(user=user, table="passwords")
            elif feature == "Sort":
                data = sqlite.queryData(user=user, table="passwords", category=category, text=None, sort_by=sort_variable)
            elif feature == "Search":
                data = sqlite.queryData(user=user, table="passwords") #, category=feature_variable[0], text=feature_variable[1], sort_by=None)

            # Loop through query data and insert relevant data to passwords_list
            for i, password in enumerate(data):
                passwords_list.append([i + 1, password[1], password[2], password[3], password[6]])

            # Find available space to size columns with first column (Index) constant and 10 spaces to the right
            column_width = (context_window.getmaxyx()[1] - 20) // (len(headers) - 1)

            # Need to erase contents of context_window to avoid new texts overwriting previous text
            context_window.erase()
            context_window.border(0)

            # Initialize current_row
            current_row = 0

            # Track the starting index for visible rows
            start_index = 0

            # Maximum rows visible within the context window
            max_visible_rows = context_window.getmaxyx()[0] - 5

            # Display headers
            context_window.addstr(3, 2, f"{headers[0]:<10}{headers[1]:<{column_width}}{headers[2]:<{column_width}}{headers[3]:<{column_width}}{headers[4]:<{column_width}}", curses.A_BOLD)
            context_window.refresh()

            # Main input loop
            while True:

                # Display options with highlighted state based on current_row
                for i, option in enumerate(options):
                    if current_row == i:
                        context_window.attron(curses.A_REVERSE)
                        context_window.addstr(1, 2 + (column_width * i), f"{option}")
                        context_window.attroff(curses.A_REVERSE)
                    else:
                        context_window.addstr(1, 2 + (column_width * i), f"{option}")

                # Ensure start_index is within valid range
                start_index = max(0, min(start_index, len(passwords_list) - max_visible_rows))

                # Get the slice of data to display
                visible_passwords = passwords_list[start_index:start_index + max_visible_rows]

                # Display the data rows with scrolling
                for i, row in enumerate(visible_passwords):
                    row_index = i + 4
                    is_selected = (start_index + i) == (current_row - len(options))

                    if is_selected:
                        context_window.attron(curses.A_REVERSE)

                    context_window.addstr(row_index, 2, f"{row[0]:<10}{row[1]:<{column_width}}{row[2]:<{column_width}}{row[3]:<{column_width}}{row[4]:<{column_width}}")

                    if is_selected:
                        context_window.attroff(curses.A_REVERSE)

                context_window.refresh()

                context_window.keypad(True)
                # Get user input
                key = context_window.getch()

                # Go to first row of table data if DOWN is pressed while current_row == any option
                if 0 <= current_row <= (len(options) - 1) and key == curses.KEY_DOWN:
                    current_row = len(options)

                # Go to first option if UP is pressed while current_row is first row of table data
                elif current_row == len(options) and key == curses.KEY_UP:
                    current_row = 0

                # Navigate through options using LEFT and RIGHT
                elif 0 <= current_row <= (len(options) - 2) and key == curses.KEY_RIGHT:
                    current_row += 1
                elif 1 <= current_row <= (len(options) - 1) and key == curses.KEY_LEFT:
                    current_row -= 1

                # Go back to first row of table data if DOWN is pressed while current_row is last row of table data
                elif current_row == (len(passwords_list) + len(options) - 1) and key == curses.KEY_DOWN:
                    current_row = len(options)  # Reset to first row of table data
                    start_index = 0             # Reset scroll to the top

                # Scroll down
                elif key == curses.KEY_DOWN:
                    if current_row < (len(passwords_list) + len(options) - 1):
                        current_row += 1
                        if (current_row - len(options)) >= (start_index + max_visible_rows):
                            start_index += 1

                # Scroll up
                elif key == curses.KEY_UP:
                    if current_row > 0:
                        current_row -= 1
                        if (current_row - len(options)) < start_index:
                            start_index -= 1

                # Enter key to select an option
                elif key == 10:
                    if current_row == 0:
                        inputs = createPassword()
                        if inputs:  # User clicked Create, not Cancel
                            # Extract fields: [Category, Account, Username, Password]
                            category = inputs[0]
                            account = inputs[1]
                            username = inputs[2]
                            plaintext_password = inputs[3]

                            # Encrypt password using session key
                            encrypted_password = CLI_Guard.encryptPassword(plaintext_password)

                            # Save to database
                            sqlite.insertData(user, category, account, username, encrypted_password)

                            # Show success message
                            message_window.erase()
                            message_window.border(0)
                            message_window.addstr(1, 2, f"Password for {account} created successfully")
                            message_window.refresh()

                            # Refresh password list
                            break
                        # Redraw the headers after popup closes
                        drawHeaders(context_window, headers, column_width)
                    elif current_row == 1:
                        category, search_term = searchPasswords(column_width)
                        feature = "Search" if category and search_term else None
                        break  # Restart with search applied
                    elif current_row == 2:
                        category, sort_variable = sortPasswords(column_width)
                        feature = "Sort" if category and sort_variable else None
                        break  # Restart with sorting applied
                    else:
                        # Fetch the actual table data row using current_row index (adjusted for the length of options list)
                        selected_record = passwords_list[current_row - len(options)]

                        # Get the original data row to access encrypted password
                        data_index = selected_record[0] - 1  # Convert display index back to 0-based
                        original_record = data[data_index]

                        # Extract encrypted password and decrypt it
                        encrypted_password = original_record[4]
                        try:
                            decrypted_password = CLI_Guard.decryptPassword(encrypted_password)

                            # Display record info with decrypted password
                            message_window.erase()
                            message_window.border(0)
                            message_window.addstr(1, 2, f"Category: {selected_record[1]}")
                            message_window.addstr(2, 2, f"Account: {selected_record[2]}")
                            message_window.addstr(3, 2, f"Username: {selected_record[3]}")
                            message_window.addstr(4, 2, f"Password: {decrypted_password}")
                            message_window.addstr(5, 2, f"Last Modified: {selected_record[4]}")
                            message_window.refresh()
                        except Exception as e:
                            # Handle decryption errors
                            message_window.erase()
                            message_window.border(0)
                            message_window.addstr(1, 2, f"Error decrypting password: {str(e)}")
                            message_window.refresh()

                # Escape key (ASCII value 27) to return to Main Menu
                elif key == 27:
                    # Clear and redraw context_window
                    context_window.erase()
                    context_window.border(0)
                    context_window.refresh()

                    # Clear and redraw message_window
                    message_window.erase()
                    message_window.border(0)
                    message_window.refresh()
                    
                    # Break the loop after exiting
                    running = False
                    break



    def createPassword(inputFields=None):
        message_window.erase()
        message_window.border(0)
        message_window.refresh()

        popup_window_panel.show()

        fields = ["Category:", "Account:", "Username:", "Password:"]
        inputs = ["" for _ in fields]

        options = ["Scramble Password", "Generate Random", "Generate Passphrase"]
        buttons = ["Create", "Cancel"]

        current_field = 0
        current_option = 0
        current_button = 0

        in_buttons = False
        in_options = False

        popup_window.keypad(True)

        running = True

        while running:
            popup_window.erase()
            popup_window.border(0)

            # Draw fields and current inputs
            for i, field in enumerate(fields):
                popup_window.addstr(2 + i, 2, field)
                popup_window.addstr(2 + i, 20, inputs[i])

                # Highlight active input
                if not in_buttons and not in_options and current_field == i:
                    popup_window.addstr(2 + i, 2, field, curses.A_REVERSE)

            # Draw options (above buttons)
            for i, option in enumerate(options):
                popup_window.addstr(8, 2 + i * 18, f"{option:^18}")

                # Highlight active option
                if in_options and current_option == i:
                    popup_window.addstr(8, 2 + i * 18, f"{option:^18}", curses.A_REVERSE)

            # Draw buttons
            for i, button in enumerate(buttons):
                popup_window.addstr(10, 20 + i * 12, button)

                # Highlight active button
                if in_buttons and current_button == i:
                    popup_window.addstr(10, 20 + i * 12, button, curses.A_REVERSE)

            popup_window.refresh()

            key = popup_window.getch()

            if key == curses.KEY_DOWN:
                if not in_buttons and not in_options:
                    current_field += 1
                    if current_field >= len(fields):
                        in_options = True
                        current_field = 0
                elif in_options:
                    in_options = False
                    in_buttons = True
                else:
                    current_button = (current_button + 1) % len(buttons)

            elif key == curses.KEY_UP:
                if in_buttons:
                    in_buttons = False
                    in_options = True
                elif in_options:
                    in_options = False
                else:
                    current_field = max(0, current_field - 1)

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

            elif not in_buttons and not in_options and 32 <= key <= 126:  # Typing in the active field
                inputs[current_field] += chr(key)

            elif key in (curses.KEY_BACKSPACE, 127, 8):  # Handle backspace (covering multiple cases)
                if not in_buttons and not in_options and inputs[current_field]:
                    inputs[current_field] = inputs[current_field][:-1]

            elif key == 10:  # Enter key
                if in_buttons:
                    if current_button == 1:  # Cancel
                        context_window.erase()
                        context_window.border(0)
                        context_window.refresh()

                        popup_window_panel.hide()
                        running = False
                    elif current_button == 0:  # Create
                        return inputs
                elif in_options:
                    # Handle selected option action (e.g., scramble, generate random, etc.)
                    if current_option == 0:
                        inputs[current_field] = "[Scrambled Password]"
                    elif current_option == 1:
                        inputs[current_field] = "[Random Password]"
                    elif current_option == 2:
                        inputs[current_field] = "[Passphrase]"

                elif key == 27:  # ESC key
                    context_window.erase()
                    context_window.border(0)
                    context_window.refresh()

                    popup_window_panel.hide()
                    running = False



    def sortPasswords(width, category=None):
        # Menu options
        options = ["Category", "Account", "Username"]
        sort_order = ["Ascending", "Descending"]

        sort_menu = curses.newwin(len(options) + 5, 15, 12, width * 3)
        sort_menu.border(0)
        sort_menu_panel = curses.panel.new_panel(sort_menu)

        sort_menu_panel.show()

        sort_menu.addstr(1, 2, "Sort By:")

        current_row = 0

        while True:
            # Display the menu
            for i, option in enumerate(options):
                if i == current_row:
                    sort_menu.attron(curses.A_REVERSE)
                sort_menu.addstr(i + 3, 2, option)
                if i == current_row:
                    sort_menu.attroff(curses.A_REVERSE)

                if current_row == len(options):
                    # Highlight the selected option
                    sort_menu.attron(curses.A_REVERSE)
                    sort_menu.addstr(len(options) + 4, 3, "| BACK |")
                    sort_menu.attroff(curses.A_REVERSE)
                else:
                    sort_menu.addstr(len(options) + 4, 3, "| BACK |", curses.color_pair(4))

            sort_menu.refresh()

            sort_menu.keypad(True)
            # Get user input
            key = sort_menu.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(options):
                current_row += 1

            # Handle Back option or ESC key
            elif key == 27 or (key == 10 and current_row == len(options)):
                sort_menu_panel.hide()
                return None, None

            # If an option is selected
            elif key == 10:
                sort_category = options[current_row]

                # Ask for ascending/descending
                sort_menu.erase()
                sort_menu.border(0)
                sort_menu.addstr(1, 2, f"Sort By")
                sort_menu.addstr(2, 2, f"{sort_category}:")
                current_row = 0

                while True:
                    # Display the menu
                    for i, option in enumerate(sort_order):
                        if i == current_row:
                            sort_menu.attron(curses.A_REVERSE)
                        sort_menu.addstr(i + 4, 2, option)
                        if i == current_row:
                            sort_menu.attroff(curses.A_REVERSE)

                        if current_row == len(sort_order):
                            # Highlight the selected option
                            sort_menu.attron(curses.A_REVERSE)
                            sort_menu.addstr(len(sort_order) + 5, 3, "| BACK |")
                            sort_menu.attroff(curses.A_REVERSE)
                        else:
                            sort_menu.addstr(len(sort_order) + 5, 3, "| BACK |", curses.color_pair(4))

                    sort_menu.refresh()

                    sort_menu.keypad(True)
                    # Get user input
                    key = sort_menu.getch()

                    if key == curses.KEY_UP and current_row > 0:
                        current_row -= 1
                    elif key == curses.KEY_DOWN and current_row < len(sort_order):
                        current_row += 1
                    elif key == 27 or (key == 10 and current_row == len(sort_order)):
                        sort_menu_panel.hide()
                        return None, None
                    elif key == 10:
                        sort_menu_panel.hide()
                        return sort_category, sort_order[current_row]



    def searchPasswords(width):
        # Search menu options
        options = ["Category", "Account", "Username"]

        search_menu = curses.newwin(len(options) + 5, 27, 12, width * 3)
        search_menu.border(0)
        search_menu_panel = curses.panel.new_panel(search_menu)

        search_menu_panel.show()

        search_menu.addstr(1, 2, "Search By:")

        current_row = 0

        while True:
            # Display the menu
            for i, option in enumerate(options):
                if i == current_row:
                    search_menu.attron(curses.A_REVERSE)
                search_menu.addstr(i + 3, 2, option)
                if i == current_row:
                    search_menu.attroff(curses.A_REVERSE)

            # Display back option with blue color
            if current_row == len(options):
                search_menu.attron(curses.A_REVERSE)
            search_menu.addstr(len(options) + 4, 3, "| BACK |", curses.color_pair(4))
            if current_row == len(options):
                search_menu.attroff(curses.A_REVERSE)

            search_menu.refresh()

            search_menu.keypad(True)
            key = search_menu.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row <= len(options):
                current_row += 1

            # Handle Back option or ESC key
            elif key == 27 or (key == 10 and current_row == len(options)):
                search_menu_panel.hide()
                return None, None

            # If an option is selected
            elif key == 10:
                search_field = options[current_row]

                # Ask for search term
                search_menu.erase()
                search_menu.border(0)
                search_menu.addstr(1, 2, f"Search {search_field} for:")

                input_row = 3
                buttons = ["| SEARCH |", "| BACK |"]

                search_term = ""
                button_index = 0
                input_mode = True  # True: Typing, False: Button Navigation

                while True:
                    # Display input field
                    search_menu.addstr(input_row, 2, search_term + " ")

                    # Display SEARCH and BACK buttons with color pair 4
                    for i, button in enumerate(buttons):
                        if i == button_index:
                            search_menu.attron(curses.A_REVERSE)
                        search_menu.addstr(len(options) + 4, 3 + (i * 13), button, curses.color_pair(4))
                        if i == button_index:
                            search_menu.attroff(curses.A_REVERSE)

                    search_menu.refresh()

                    key = search_menu.getch()

                    if input_mode:
                        if key in (curses.KEY_BACKSPACE, 127, 8):  # Handle backspace
                            search_term = search_term[:-1]
                        elif key == 27:  # ESC key to cancel
                            search_menu_panel.hide()
                            return None, None
                        elif key == curses.KEY_DOWN:  # Move to button navigation
                            input_mode = False
                        elif 32 <= key <= 126:  # Typing input (printable ASCII)
                            search_term += chr(key)
                            search_menu.refresh()  # Refresh to show the typed character
                    else:  # Button navigation
                        if key == curses.KEY_UP:
                            button_index = 0  # Move back to input mode
                            input_mode = True
                        elif key == curses.KEY_DOWN and button_index < len(buttons) - 1:
                            button_index += 1
                        elif key == curses.KEY_UP and button_index > 0:
                            button_index -= 1
                        elif key == 10:
                            if button_index == 0:  # SEARCH
                                search_menu_panel.hide()
                                return search_field, search_term
                            elif button_index == 1:  # BACK
                                search_menu_panel.hide()
                                return None, None
                        elif key == 27:  # ESC key to cancel
                            search_menu_panel.hide()
                            return None, None




    def userManagement():
        
        user_menu_panel.show()

        # Menu options
        options = ["Create User", "Update User", "Delete User"]
        current_row = 0

        while True:

            # Display the menu
            for i, option in enumerate(options):
                if i == current_row:
                    # Highlight the selected option
                    user_menu.attron(curses.A_REVERSE)
                    user_menu.addstr(i + 1, 2, option)
                    user_menu.attroff(curses.A_REVERSE)
                else:
                    user_menu.addstr(i + 1, 2, option)
        
                if current_row == len(options):
                    # Highlight the selected option
                    user_menu.attron(curses.A_REVERSE)
                    user_menu.addstr(len(options) + 2, 3, "| BACK |")
                    user_menu.attroff(curses.A_REVERSE)
                else:
                    user_menu.addstr(len(options) + 2, 3, "| BACK |", curses.color_pair(4))

            user_menu.refresh()

            user_menu.keypad(True)
            # Get user input
            key = user_menu.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(options):
                current_row += 1
            elif key == 27 or (key == 10 and current_row == len(options)):
                # Clear and redraw context_window
                context_window.erase()
                context_window.border(0)
                context_window.refresh()

                # Clear and redraw message_window
                message_window.erase()
                message_window.border(0)
                message_window.refresh()

                user_menu_panel.hide()
                # Break the loop after exiting
                break
            elif key == 10:  # ASCII value for Enter key
                # Call the function corresponding to the selected option
                message_window.erase()
                message_window.border(0)
                message_window.addstr(1, 2, f"User selected {options[current_row]} button")
                message_window.refresh()


    def migrateDatabase():

        migration_menu_panel.show()

        # Menu options
        options = ["Export Database", "Import Database"]
        current_row = 0

        while True:

            # Display the menu
            for i, option in enumerate(options):
                if i == current_row:
                    # Highlight the selected option
                    migration_menu.attron(curses.A_REVERSE)
                    migration_menu.addstr(i + 1, 2, option)
                    migration_menu.attroff(curses.A_REVERSE)
                else:
                    migration_menu.addstr(i + 1, 2, option)

                if current_row == len(options):
                    # Highlight the selected option
                    migration_menu.attron(curses.A_REVERSE)
                    migration_menu.addstr(len(options) + 2, 3, "| BACK |")
                    migration_menu.attroff(curses.A_REVERSE)
                else:
                    migration_menu.addstr(len(options) + 2, 3, "| BACK |", curses.color_pair(4))

            migration_menu.refresh()

            migration_menu.keypad(True)
            # Get user input
            key = migration_menu.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(options):
                current_row += 1
            elif key == 27 or (key == 10 and current_row == len(options)):
                # Clear and redraw context_window
                context_window.erase()
                context_window.border(0)
                context_window.refresh()

                # Clear and redraw message_window
                message_window.erase()
                message_window.border(0)
                message_window.refresh()

                migration_menu_panel.hide()
                # Break the loop after exiting
                break
            elif key == 10:  # ASCII value for Enter key
                # Call the function corresponding to the selected option
                message_window.erase()
                message_window.border(0)
                message_window.addstr(1, 2, f"User selected {options[current_row]} button")
                message_window.refresh()


    def settingsManagement():

        settings_menu_panel.show()

        # Menu options
        options = ["Scrambler", "Random Generator", "Passphrases"]
        current_row = 0

        while True:

            # Display the menu
            for i, option in enumerate(options):
                if i == current_row:
                    # Highlight the selected option
                    settings_menu.attron(curses.A_REVERSE)
                    settings_menu.addstr(i + 1, 2, option)
                    settings_menu.attroff(curses.A_REVERSE)
                else:
                    settings_menu.addstr(i + 1, 2, option)

                if current_row == len(options):
                    # Highlight the selected option
                    settings_menu.attron(curses.A_REVERSE)
                    settings_menu.addstr(len(options) + 2, 3, "| BACK |")
                    settings_menu.attroff(curses.A_REVERSE)
                else:
                    settings_menu.addstr(len(options) + 2, 3, "| BACK |", curses.color_pair(4))

            settings_menu.refresh()

            settings_menu.keypad(True)
            # Get user input
            key = settings_menu.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(options):
                current_row += 1
            elif key == 27 or (key == 10 and current_row == len(options)):
                # Clear and redraw context_window
                context_window.erase()
                context_window.border(0)
                context_window.refresh()

                # Clear and redraw message_window
                message_window.erase()
                message_window.border(0)
                message_window.refresh()

                settings_menu_panel.hide()
                # Break the loop after exiting
                break
            elif key == 10:  # ASCII value for Enter key
                # Call the function corresponding to the selected option
                message_window.erase()
                message_window.border(0)
                message_window.addstr(1, 2, f"User selected {options[current_row]} button")
                message_window.refresh()


    def signOut():
        # End the session and clear encryption key
        CLI_Guard.endSession()

        context_window.erase()
        context_window.border(0)
        context_window.addstr(3, 3, "Signed out successfully. Goodbye!")
        context_window.refresh()
        time.sleep(1)

        # Return a signal to break the menu loop
        return "SIGN_OUT"
    

    def quitMenu():
        context_window.erase()
        context_window.border(0)
        context_window.addstr(3, 3, "Quitting...")
        context_window.refresh()
        time.sleep(0.5)
        exit()


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

        menu_window.refresh()

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
            # Call the function corresponding to the selected option
            result = functions[current_row]()
            # Check if sign-out was selected
            if result == "SIGN_OUT":
                break



def main(stdscr):
    """Main entry point"""
    # Disable cursor and enable keypad input
    curses.curs_set(0)
    stdscr.keypad(True)

    # Create all windows once
    windows = createWindows(stdscr)

    # Main application loop - allows returning to sign-in after sign-out
    while True:
        # Sign in
        user = signIn(windows)

        if user is None:
            return  # User chose to quit

        # Extract windows for menu
        menu_window = windows['menu_window']
        message_window = windows['message_window']
        user_menu = windows['user_menu']
        user_menu_panel = windows['user_menu_panel']
        migration_menu = windows['migration_menu']
        migration_menu_panel = windows['migration_menu_panel']
        settings_menu = windows['settings_menu']
        settings_menu_panel = windows['settings_menu_panel']
        popup_window = windows['popup_window']
        popup_window_panel = windows['popup_window_panel']
        context_window = windows['context_window']

        # Clear and update menu window with current user
        menu_window.erase()
        menu_window.border(0)
        menu_window.addstr(1, 2, "MAIN MENU")
        menu_window.addstr(menu_window.getmaxyx()[0] - 4, 2, "Current User:")
        menu_window.addstr(menu_window.getmaxyx()[0] - 3, 2, f"{user}")

        # Draw initial windows
        windows['main_win'].noutrefresh()
        windows['logo_window'].noutrefresh()
        message_window.noutrefresh()
        menu_window.noutrefresh()
        migration_menu.noutrefresh()
        context_window.noutrefresh()
        curses.doupdate()

        # Start main menu
        mainMenu(menu_window, message_window, user_menu, user_menu_panel, migration_menu, migration_menu_panel, settings_menu, settings_menu_panel, popup_window, popup_window_panel, context_window, user)

        # After mainMenu exits (sign-out), clear windows and loop back to sign-in
        menu_window.erase()
        menu_window.border(0)
        menu_window.refresh()
        context_window.erase()
        context_window.border(0)
        context_window.refresh()
        message_window.erase()
        message_window.border(0)
        message_window.refresh()

curses.wrapper(main)