# Import curses for Terminal User Interface and navigation
# https://docs.python.org/3/library/curses.html
import curses
import curses.panel

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
    menu_window = curses.newwin(height - 12, 21, 10, 0)
    menu_window.border(0)
    context_window = curses.newwin(height - 12, width - 21, 10, 21)
    context_window.border(0)

    # Print the Logo to logo_window
    displayLogo(logo_window)

    # Display text in other windows
    message_window.addstr(1, 2, "MESSAGE WINDOW")
    menu_window.addstr(1, 2, "MENU WINDOW")
    context_window.addstr(1, 2, "CONTEXT WINDOW")

    # Use noutrefresh() to update all windows together
    main_win.noutrefresh()
    logo_window.noutrefresh()
    message_window.noutrefresh()
    menu_window.noutrefresh()
    context_window.noutrefresh()

    # Update screen
    curses.doupdate()

    # Now, safely call the mainMenu without hiding other windows
    mainMenu(menu_window, context_window)

    # Wait for user input to exit
    main_win.getch()



def mainMenu(menu_window, context_window):

    # Disable cursor and enable keypad input
    curses.curs_set(0)
    menu_window.keypad(True)

    # Define functions for each option
    def option1():

        # Need to erase contents of context_window to avoid new texts overwriting previous text
        # but this also erases the broder and heading which need to be reprinted
        context_window.erase()
        context_window.border(0)
        context_window.addstr(1, 2, "CONTEXT WINDOW")

        context_window.addstr(3, 3, "User selected Create Password")
        context_window.refresh()
    
    def option2():
        context_window.erase()
        context_window.border(0)
        context_window.addstr(1, 2, "CONTEXT WINDOW")

        context_window.addstr(3, 3, "User selected Edit Password")
        context_window.refresh()

    def option3():
        context_window.erase()
        context_window.border(0)
        context_window.addstr(1, 2, "CONTEXT WINDOW")

        context_window.addstr(3, 3, "User selected Delete Password")
        context_window.refresh()

    def option4():
        context_window.erase()
        context_window.border(0)
        context_window.addstr(1, 2, "CONTEXT WINDOW")

        context_window.addstr(3, 3, "User selected Display Passwords")
        context_window.refresh()

    def option5():
        context_window.erase()
        context_window.border(0)
        context_window.addstr(1, 2, "CONTEXT WINDOW")

        context_window.addstr(3, 3, "User selected User Management")
        context_window.refresh()

    def option6():
        context_window.erase()
        context_window.border(0)
        context_window.addstr(1, 2, "CONTEXT WINDOW")

        context_window.addstr(3, 3, "User selected Migrate Database")
        context_window.refresh()

    def option7():
        context_window.erase()
        context_window.border(0)
        context_window.addstr(1, 2, "CONTEXT WINDOW")

        context_window.addstr(3, 3, "User selected Sign Out")
        context_window.refresh()
    
    def option8():
        context_window.erase()
        context_window.border(0)
        context_window.addstr(1, 2, "CONTEXT WINDOW")

        context_window.addstr(3, 3, "User selected Quit")
        context_window.refresh()
        exit()

    # Menu options
    options = ["Create Password", "Edit Password", "Delete Password", "Display Passwords", "User Management", "Migrate Database", "Sign Out", "Quit"]
    current_row = 0

    # Map menu options to functions
    functions = {
        0: option1,
        1: option2,
        2: option3,
        3: option4,
        4: option5,
        5: option6,
        6: option7,
        7: option8
    }

    while True:

        # Display the menu
        for idx, option in enumerate(options):
            if idx == current_row:
                # Highlight the selected option
                menu_window.attron(curses.A_REVERSE)
                menu_window.addstr(idx + 3, 2, option)
                menu_window.attroff(curses.A_REVERSE)
            else:
                menu_window.addstr(idx + 3, 2, option)

        menu_window.refresh()

        # Get user input
        key = menu_window.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) - 1:
            current_row += 1
        elif key == 10:  # Enter key
            # Call the function corresponding to the selected option
            functions[current_row]()



def main(stdscr):

    # Disable cursor and enable keypad input
    curses.curs_set(0)
    stdscr.keypad(True)

    createWindows(stdscr)

curses.wrapper(main)