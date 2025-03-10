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

    user_menu = curses.newwin(6, 21, 12, 21)
    user_menu.border(0)
    user_menu_panel = curses.panel.new_panel(user_menu)
    user_menu_panel.hide()

    migration_menu = curses.newwin(5, 21, 13, 21)
    migration_menu.border(0)
    migration_menu_panel = curses.panel.new_panel(migration_menu)
    migration_menu_panel.hide()

    settings_menu = curses.newwin(6, 21, 14, 21)
    settings_menu.border(0)
    settings_menu_panel = curses.panel.new_panel(settings_menu)
    settings_menu_panel.hide()

    context_window = curses.newwin(height - 10, width - 21, 10, 21)
    context_window.border(0)

    # Print the Logo to logo_window
    displayLogo(logo_window)

    user = None # CHANGE THIS / FIX THIS
    menu_window.addstr(0, 2, "MAIN MENU")
    # Display Current User information in the fourth and third last available row of the Terminal
    menu_window.addstr(menu_window.getmaxyx()[0] - 4, 2, "Current User:")
    menu_window.addstr(menu_window.getmaxyx()[0] - 3, 2, f"{user}")

    # Use noutrefresh() to update all windows together
    main_win.noutrefresh()
    logo_window.noutrefresh()
    message_window.noutrefresh()
    menu_window.noutrefresh()
    migration_menu.noutrefresh()
    context_window.noutrefresh()

    # Update screen
    curses.doupdate()

    mainMenu(menu_window, context_window, message_window, user_menu, user_menu_panel, migration_menu, migration_menu_panel, settings_menu, settings_menu_panel)



def mainMenu(menu_window, context_window, message_window, user_menu, user_menu_panel, migration_menu, migration_menu_panel, settings_menu, settings_menu_panel):

    # Disable cursor and enable keypad input
    curses.curs_set(0)
    menu_window.keypad(True)

    def get_user_input(window, prompt):
        window.clear()
        window.border(0)
        window.addstr(1, 2, prompt)
        window.refresh()

        # Get user input (max length of 50 characters in this case)
        curses.echo()  # Allow typed input to be visible
        user_input = window.getstr(2, 2, 50).decode('utf-8')
        curses.noecho()  # Hide input again

        return user_input

    # Define functions for each option
    def passwordManagement():
        options = ["Create Password", "Search Passwords", "Sort Passwords"]
        headers = ["Index", "Name", "Age", "Country"]
        data = [
            [1, "John Doe", 28, "USA"],
            [2, "Jane Smith", 34, "Canada"],
            [3, "Sam Brown", 22, "UK"],
            [4, "Lucy Green", 29, "Australia"],
            [5, "David White", 45, "Ireland"],
            [6, "Emily Black", 37, "USA"],
            [7, "Michael Blue", 50, "Canada"],
            [8, "Sophia Yellow", 31, "UK"],
            [9, "James Red", 40, "Australia"],
            [10, "Olivia Purple", 25, "Ireland"],
            [11, "Noah Orange", 33, "USA"],
            [12, "Ava Pink", 41, "Canada"],
        ]

        # Find available space to size columns with first column (Index) constant and 10 spaces to the right
        column_width = (context_window.getmaxyx()[1] - 20) // (len(headers) - 1)
        
        # Need to erase contents of context_window to avoid new texts overwriting previous text
        context_window.erase()
        context_window.border(0)

        # Initialize current_row
        current_row = 0

        # Display headers
        context_window.addstr(3, 2, f"{headers[0]:<10}{headers[1]:<{column_width}}{headers[2]:<{column_width}}{headers[3]:<{column_width}}")
        context_window.refresh()

        while True:
            # Display options with highlighted state based on current_row
            for i, option in enumerate(options):
                if current_row == i:
                    context_window.attron(curses.A_REVERSE)
                    context_window.addstr(1, 2 + (column_width * i), f"{option}")
                    context_window.attroff(curses.A_REVERSE)
                else:
                    context_window.addstr(1, 2 + (column_width * i), f"{option}")
            
            # Display the data rows, starting from the 4th row (after the headers and options)
            for i, row in enumerate(data):
                # Start displaying data from row 4 (index 3 is for options and headers)
                row_index = i + 4
                if current_row == i + 3:
                    # Highlight the selected data row based on current_row
                    context_window.attron(curses.A_REVERSE)
                    context_window.addstr(row_index, 2, f"{row[0]:<10}{row[1]:<{column_width}}{row[2]:<{column_width}}{row[3]:<{column_width}}")
                    context_window.attroff(curses.A_REVERSE)
                else:
                    context_window.addstr(row_index, 2, f"{row[0]:<10}{row[1]:<{column_width}}{row[2]:<{column_width}}{row[3]:<{column_width}}")

            context_window.refresh()

            # Get user input
            key = menu_window.getch()

            # Navigate through options separatley using LEFT and RIGHT
            if 0 <= current_row <= (len(options) - 2) and key == curses.KEY_RIGHT:
                current_row += 1
            elif 1 <= current_row <= (len(options) - 1) and key == curses.KEY_LEFT:
                current_row -= 1
            
            # Go to first row of table data if DOWN is pressed while current_row == any option
            elif 0 <= current_row <= (len(options) - 1) and key == curses.KEY_DOWN:
                current_row = len(options)
            # Go to last row of table data if UP is pressed while current_row == 0
            elif current_row == 0 and key == curses.KEY_UP:
                current_row = (len(data) + len(options) - 1)
            # Go to first option if UP is pressed while current_row is first row of table data
            elif current_row == len(options) and key == curses.KEY_UP:
                current_row = 0
            
            # Go back to first row of table data is DOWN is pressed while current_row is last row of table data
            elif current_row == (len(data) + len(options) - 1) and key == curses.KEY_DOWN:
                current_row = 3 

            # Navigate through table data using UP and DOWN
            elif key == curses.KEY_UP:
                current_row -= 1
            elif key == curses.KEY_DOWN:
                current_row += 1
            
            # Enter key to select an option
            elif key == 10:
                if current_row == 0:
                    create_password()
                elif current_row == 1:
                    search_passwords()
                elif current_row == 2:
                    sort_passwords()
                else:
                    # Fetch the actual table data row using current_row index (adjusted for the length of options list)
                    selected_row = data[current_row - 3]
                    message_window.addstr(1, 2, f"{selected_row[0]:<10}{selected_row[1]:<20}{selected_row[2]:<20}{selected_row[3]:<20}", curses.color_pair(6))
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
                break


    def create_password():
        message_window.erase()
        message_window.border(0)
        message_window.addstr(1, 2, "User selected Create Password button")
        message_window.refresh()


    def sort_passwords():
        message_window.erase()
        message_window.border(0)
        message_window.addstr(1, 2, "User selected Sort Passwords button")
        message_window.refresh()


    def search_passwords():
        message_window.erase()
        message_window.border(0)
        message_window.addstr(1, 2, "User selected Search Passwords button")
        message_window.refresh()


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
                    user_menu.addstr(len(options) + 2, 3, "Back")
                    user_menu.attroff(curses.A_REVERSE)
                else:
                    user_menu.addstr(len(options) + 2, 3, "Back", curses.color_pair(4))

            user_menu.refresh()

            # Get user input
            key = menu_window.getch()

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
                    migration_menu.addstr(len(options) + 2, 3, "Back")
                    migration_menu.attroff(curses.A_REVERSE)
                else:
                    migration_menu.addstr(len(options) + 2, 3, "Back", curses.color_pair(4))

            migration_menu.refresh()

            # Get user input
            key = menu_window.getch()

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
        options = ["Settings Option 1", "Settings Option 2", "Settings Option 3"]
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
                    settings_menu.addstr(len(options) + 2, 3, "Back")
                    settings_menu.attroff(curses.A_REVERSE)
                else:
                    settings_menu.addstr(len(options) + 2, 3, "Back", curses.color_pair(4))

            settings_menu.refresh()

            # Get user input
            key = menu_window.getch()

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

    def option5():
        context_window.erase()
        context_window.border(0)
        context_window.addstr(3, 3, "User selected Sign Out")
        context_window.refresh()
    
    def option6():
        context_window.erase()
        context_window.border(0)
        context_window.addstr(3, 3, "Quiting...")
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
        4: option5,
        5: option6
    }

    while True:

        # Display the menu
        for i, option in enumerate(options):
            if i == current_row:
                # Highlight the selected option
                menu_window.attron(curses.A_REVERSE)
                menu_window.addstr(i + 2, 2, option)
                menu_window.attroff(curses.A_REVERSE)
            else:
                menu_window.addstr(i + 2, 2, option)

        menu_window.refresh()

        # Get user input
        key = menu_window.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) - 1:
            current_row += 1
        elif key == 10:  # ASCII value for Enter key
            # Call the function corresponding to the selected option
            functions[current_row]()



def main(stdscr):

    # Disable cursor and enable keypad input
    curses.curs_set(0)
    stdscr.keypad(True)

    createWindows(stdscr)

curses.wrapper(main)