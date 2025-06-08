# CLI Guard SQL
import  CLI_SQL.CLI_Guard_SQL as sqlite

# Tabulate is used to output passwords_list and master_users_list data to Terminal in grid format
from tabulate import tabulate

# Import OS library
import os
insertUser
# Import Traceback for logging
import traceback

# PyperClip used to Copy to Clipboard
import pyperclip

# Readchar is used for Terminal navigation
import readchar

# Import PyGetWindow to get current window size
import pygetwindow as gw

# DateTime used when editing passwords or adding new passwords
from datetime import date, datetime, timedelta

today = date.today()
todays_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
tomorrow = date.today() + timedelta(1)

# Colour text and others
from colorama import init, Fore, Back, Style

# Initialize Colorama (autoreset restores default after print)
init(autoreset=True)

# Import Sys, Time and Threading for the Splash screen dots animation
import time
import sys
import threading

# Import Python Cryptography library and Fernet module according to documentation
from cryptography.fernet import Fernet

# Generate the Fernet Encryption Key
# Required for encryption and decryption with Fernet as per documentation
# Since the Encryption Key is generated upon each session, the session's
# Key is converted into a STRING from BITS then the string is written to
# the SQLite database for each password created or added
# We can then later use the Encryption key saved with that record to 
# Decrypt and decode the password
encryption_key = Fernet.generate_key()
fernet = Fernet(encryption_key)
session_password_key = encryption_key



# Formatting Terminal output
# Colorama in Splash uses Fore.WHITE instead of Style.RESET_ALL 
# to ensure the uncoloured components are white instead of default Terminal colour if different
splash = f"""                                                                                                      
                                                              {Fore.BLUE}███████{Fore.WHITE}   ▒█                          
                                                            {Fore.BLUE}███████████{Fore.WHITE}██                           
                                      {Fore.LIGHTBLUE_EX}██████             █████████████{Fore.WHITE}██                            
                            {Fore.LIGHTBLUE_EX}░░░   █████   ███████████████████{Fore.WHITE}        █▓                             
                                      {Fore.CYAN}████         ▓█████████{Fore.WHITE}       ██                              
                             {Fore.CYAN}░ ████████░ ██████████████▒{Fore.WHITE}           ██                               
                                              {Fore.LIGHTCYAN_EX}████{Fore.WHITE}                ██                                
                                                                 ██                                 
                                                                ██                                  
                                                               ██                                   
                                             ███              ██                                    
                                           ███████           ██                                     
                                     ███  ███    ███        ██                                      
                                   █████ ███  ████  ██     ██         █████                         
                 █                  ████████   █████████ ███      ▒█████████████                    
                █                     ░       ██████    ███  ▓███████████████████                   
               ████                         ██████  █  ████ ░██████████████████████                 
                  █████████████             ███████ ░  ██  ███████████████  ████                    
               ███  █████   ████           ██▓███████████▒█ ████████████████████                    
              ██  ████████  ▓███         ▒███              ███████████ ████████                     
              █   ███░ ████ ███▓         ████      {Fore.RED}██{Fore.WHITE}      ▒  ░██████   ██████▓                     
                ██ ▓██▓ ██████                  {Fore.RED}████████{Fore.WHITE}  █       ▒███ ██████                      
               ██ ████  █████            █████     {Fore.RED}██{Fore.WHITE}      █ █ ██ ██    ██ ███                      
                 █████▒████              █████     {Fore.RED}██{Fore.WHITE}    █████ ▓█  █▓  ▓██                        
                     ██████       ░████████████           █████████▒██ ██                           
                     █████████████████░  █████████      ██ ██████████████       ███                 
                      ██████▓  ██████            ████████  █████████████████████████              
                              ███████                   █  █████████████████████ ███               
                             ████████                    █  ███████████████  ███ ███                
                             ███████                     ██ ███████         ██   ███               
                             ░████▒  █         █    █   ██▒   █           ███    ███               
                              ███  ░█   ███  ███  ███ ███████▒ ██      █████  ░███                  
                               ██████ ████  ███▒██████                ░███    ███                   
                               ██████████████████                                                   
                            ███████████  ██████                                                     
                          █████████   ██████         {Fore.BLUE}██████╗ ██╗      ██╗     ██████╗  ██╗   ██╗  █████╗  ██████╗  ██████╗{Fore.WHITE}
                       ████████    ██████           {Fore.BLUE}██╔════╝ ██║      ██║    ██╔════╝  ██║   ██║ ██╔══██╗ ██╔══██╗ ██╔══██╗{Fore.WHITE}
                        ████        █████           {Fore.LIGHTBLUE_EX}██║      ██║      ██║    ██║  ███╗ ██║   ██║ ███████║ ██████╔╝ ██║  ██║{Fore.WHITE}
                          ███          ████         {Fore.LIGHTBLUE_EX}██║      ██║      ██║    ██║   ██║ ██║   ██║ ██╔══██║ ██╔══██╗ ██║  ██║{Fore.WHITE}
                            ████         ▒███▓      {Fore.CYAN}╚██████╗ ███████╗ ██║    ╚██████╔╝ ╚██████╔╝ ██║  ██║ ██║  ██║ ██████╔╝{Fore.WHITE}
                             █████         ██        {Fore.LIGHTCYAN_EX}╚═════╝ ╚══════╝ ╚═╝     ╚═════╝   ╚═════╝  ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═════╝ {Fore.WHITE}
                                 ████       █████                            
"""

logo = f"""                                                                                                      
       {Fore.BLUE}██████╗ ██╗      ██╗     ██████╗  ██╗   ██╗  █████╗  ██████╗  ██████╗{Style.RESET_ALL}
      {Fore.BLUE}██╔════╝ ██║      ██║    ██╔════╝  ██║   ██║ ██╔══██╗ ██╔══██╗ ██╔══██╗{Style.RESET_ALL}
      {Fore.LIGHTBLUE_EX}██║      ██║      ██║    ██║  ███╗ ██║   ██║ ███████║ ██████╔╝ ██║  ██║{Style.RESET_ALL}
      {Fore.LIGHTBLUE_EX}██║      ██║      ██║    ██║   ██║ ██║   ██║ ██╔══██║ ██╔══██╗ ██║  ██║{Style.RESET_ALL}
      {Fore.CYAN}╚██████╗ ███████╗ ██║    ╚██████╔╝ ╚██████╔╝ ██║  ██║ ██║  ██║ ██████╔╝{Style.RESET_ALL}
       {Fore.LIGHTCYAN_EX}╚═════╝ ╚══════╝ ╚═╝     ╚═════╝   ╚═════╝  ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═════╝ {Style.RESET_ALL}                  
"""


# Not all message-pieces should be kept in a list
# Overuse of lists for message-pieces makes creating messages confusing
done = ["ed password for ", "...\n"]
navigation_text = f"{Fore.CYAN}\nUse ↑ and ↓ to navigate\nPress Enter to select\n{Style.RESET_ALL}"
features = f"{Fore.CYAN}Return to Main Menu using ESC\nSearch using CTRL + F\nSort using CTRL + S\n{Style.RESET_ALL}"
splash_continue = f"Press Enter to continue..."


# Create empty list of users and encrypted passwords
passwords_list = []
master_users_list = []
# Initialise feature_variable as List to accept multiple arguments
feature_variable = []
# Initialise mode
mode = ""



# Write to Log file
def logging(message=None) -> None:
    with open(os.path.join(".", "Logs.txt"), "a") as file:
        #  Handles Traceback since no message argument is passed
        if message is None:
            # traceback.format_exc() function works without explicitly passing an error
            # because it captures the most recent exception from the current context
            file.write(f"[{todays_time}] {traceback.format_exc()}\n")
        else:
            # Handles Logging when a message argument is passed
            file.write(f"[{todays_time}] {message}\n")


def accountLocked(master_users_list, selected_index) -> bool:
    try:
        if str(master_users_list[selected_index][-1]) == str(today):
            return True
    except Exception:
        logging()


def listNotEmpty(list) -> bool:
    try:
        return list != []
    except Exception:
        logging()


# Clear Terminal and print Logo
# Avoids multiple lines of code each time a screen clear and logo print are required
# Not all calls to logoScreen require a statement
# and when a statement is not provided "None" is printed to screen
def logoScreen(logo_statement=None) -> None:
    try:
        os.system("cls")
        if logo_statement is None:
            print(f"{logo}")
        else:
            print(f"{logo}\n{logo_statement}")
    except Exception:
        logging()


# User input via keyboard to continue
# this avoids the print statement clearing before user reads it
# enterContinue() needs to be called as an if statement since pressing Enter returns True
def enterContinue(enter_continue_statement) -> bool:
    try:
        # split(' ', 2)[1] matches enter_continue_statement on second word instead of full text
        # to capture password_list is empty as well as Database Migration functions
        if enter_continue_statement.split(' ', 2)[1] in [ "are", "exported", "imported"]:
            continue_action = "return to Start Menu"
        # Don't print return to Start Menu message if creating Master User for first time
        # Needs to skip case where enter_continue_statement == "A Master User already exists with this name"
        # since the above case needs to print Try Again message
        # ' '.join(enter_continue_statement(' ', 2)[:2]) matches enter_continue_statement
        # on first 2 words instead of full text to capture 1 case
        elif ' '.join(enter_continue_statement.split(' ', 2)[:2]) == "No Master":
            continue_action = "create new Mater User"
        # This is handled separately from the catch all else statement since case "Master User cannot be empty"
        # is captured incorrectly unless evaulated before the next elif statement but needs to print Try Again message
        # split(' ', 3)[2] matches enter_continue_statement on third word instead of full text
        elif enter_continue_statement.split(' ', 3)[2] == "cannot":
            continue_action = "try again"
        # Handles current user switch when creating new Master Users
        # Handles when updating password for current Master User
        elif enter_continue_statement.split(' ', 2)[1] == "User":
            continue_action = "Sign In"
        # Handles all other scenarios
        else:
            continue_action = "try again"

        logoScreen(logo_statement=f"\n{enter_continue_statement}\n\nPress Enter to {continue_action}")
        key = readchar.readkey()
        if key == readchar.key.ENTER:
            return True
    except Exception:
        logging()


# Encryption
def encryptPassword(password) -> str:
    try:
        # Password is encoded then saved to a new variable per documentation
        encrypted_password = fernet.encrypt(password.encode())
        # The variable needs var.decode() when adding to the encrypted passwords table
        # This converts the values datatype from BITS to STRING
        # Otherwise it saves to the list as b'var' instead of 'var'
        # Decode is different to Decrypt, remember to read the docs more
        # The encoded password is BITS datatype once encrypted and needs it's own variable
        return encrypted_password.decode()
    except Exception:
        logging()


# Decryption
def decryptPassword(encryption_key, password) -> str:
    try:
        # Decrypted password needs to be saved to its own variable
        # We use Fernet(password_key) here instead of fernet variable to
        # Decrypt with the relevant records Encryption Key
        decrypted_password = Fernet(encryption_key).decrypt(password)
        # Remember to DECODE the new variable to convert from BITS datatype to STRING
        # This removes the leading b value changing b'variable' to 'variable"
        return decrypted_password.decode()
    except Exception:
        logging()


# Maximize the terminal using pygetwindow
def maximizeTerminal() -> None:
    try:
        # Rename title for Windows
        if os.name == 'nt':
            os.system(f"title CLI Guard")
        # Rename title for macOS/Linux
        else:
            sys.stdout.write(f"\033]0;CLI Guard\007")
            sys.stdout.flush()
        
        # Get all windows and filter by titles that match the criteria
        windows = gw.getAllWindows()
        
        for window in windows:
            # Check if the title is either "Command Prompt" or contains "\cmd"
            if "CLI Guard" in window.title:
                window.maximize()
                break
    except Exception:
        logging()


# Attempt Log In if user exists
def splashScreen() -> None:
    try:
        # Maximize terminal window
        maximizeTerminal()
        # Clear Terminal then SPLASH
        os.system("cls")
        # Print CLI Guard Splash
        print(f"{splash}\nPress Enter to continue", end="", flush=True)

        # Hide cursor
        # Enable ANSI escape codes on Windows
        os.system("")
        # ANSI code to hide cursor
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        # Shared flag to control the animation
        stop_animation = threading.Event()

        def dotAnimation() -> None:
            try:
                while not stop_animation.is_set():
                    for dots in range(4):
                        if stop_animation.is_set():
                            break
                        # Print dots in sequence on loop
                        sys.stdout.write("\rPress Enter to continue" + "." * dots + "   ")
                        sys.stdout.flush()
                        time.sleep(0.4)
            except Exception:
                logging()

        # Start dot animation in a separate thread
        animation_thread = threading.Thread(target=dotAnimation, daemon=True)
        animation_thread.start()

        while True:
                key = readchar.readkey()
                if key == readchar.key.ENTER:
                    # Signal the animation thread to stop
                    stop_animation.set()
                    # Ensure the animation thread is finished before proceeding
                    animation_thread.join()
                    login()

    except Exception:
        logging()


def login() -> None:
    try:
        # Clear Terminal and print Logo
        logoScreen()
        # Query the users table and insert all into master_users_list
        master_users_list = sqlite.queryData(user=None, table="users")
        # Check if master_users_list is empty
        if listNotEmpty(master_users_list):
            selected_index = 0

            while True:
                # Append more options to the table to allow user to create a new Master User directly from login screen
                extended_list = master_users_list + [("Create New Master User", "", newMaster), ("Quit", "", exit)]

                # Display the table with navigation
                displayTable(extended_list, selected_index, table="users")

                # User input via keyboard
                key = readchar.readkey()

                if key == readchar.key.UP:
                    selected_index = (selected_index - 1) % len(extended_list)
                elif key == readchar.key.DOWN:
                    selected_index = (selected_index + 1) % len(extended_list)
                elif key == readchar.key.ENTER:
                    # newMaster and Quit do not require any arguments to be passed so are called separately
                    # Check if selected index is within the last 2 items of
                    # extended_list then execute last item in the selected tuple
                    if selected_index >= len(extended_list) - 2:
                        extended_list[selected_index][-1]()
                    else:
                        # Check if selected account is locked before attempting to login
                        if accountLocked(master_users_list, selected_index) is True:
                            if enterContinue(enter_continue_statement=f"Account {extended_list[selected_index][0]} locked until {tomorrow}") is True:
                                login()
                        else:
                            # Before decrypting the password we need to save the returned Encryption Key for that record
                            # Make number of attempted passwords 0 from Attempt Log In screen
                            attemptLogin(user=extended_list[selected_index][0], attempt=0, master_key=extended_list[selected_index][2], master_password=extended_list[selected_index][1])
        else:
            if enterContinue(enter_continue_statement="No Master Users exist yet") is True:
                newMaster()
    except Exception:
        logging()


# Log In screen to avoid splash everytime
def attemptLogin(user, attempt, master_key, master_password) -> None:
    try:
        # 3 attempts to Log In before writing to Log file and locking account for 1 day
        if attempt < 3:
            attempted_password = str(input("\nMaster password: "))
            if attempted_password:
                # Decrypt Master Password to compare with attempted_password
                decrypted_master_password = decryptPassword(master_key, master_password)
                if attempted_password == decrypted_master_password:
                    start(user)
                else:
                    # Clear Terminal and print Logo
                    logoScreen()
                    # Add attempt to attempts before returning to Log In screen
                    attempt += 1
                    print(f"{Fore.RED}Incorrect password attempted{Style.RESET_ALL}")
                    attemptLogin(user, attempt, master_key, master_password)
            else:
                if enterContinue(enter_continue_statement=f"{Fore.RED}No password was entered{Style.RESET_ALL}") is True:
                    attemptLogin(user, attempt, master_key, master_password)
        else:
            # Set last_locked to today on the users table
            sqlite.lockUser(user)
            # Write to Log file
            logging(message=f"Incorrect password entered 3 times for Master User {user} - Account {user} locked until {tomorrow}")
            # Print Account Locked notice to screen and return to Login
            if enterContinue(enter_continue_statement=f"Incorrect password entered 3 times\nAccount {user} locked until {tomorrow}") is True:
                login()
    except Exception:
        logging()


# Display Splash and Start Menu to CLI - User chooses function
def start(user) -> None:
    try:
        # Define function index, human-readable text, function name
        functions = [
            ("Create new password", addPassword),
            ("Edit a password", "Edit"),
            ("Delete a password", "Delete"),
            ("Display a password", "Decrypt"),
            ("User Management", userManagement),
            ("Migrate Database", migrateDatabase),
            ("Sign Out", login),
            ("Quit", exit)
        ]

        selected_index = 0

        def startMenu() -> None:
            try:
                # Clear Terminal and print Logo and navigation_text
                logoScreen(logo_statement=navigation_text)
                for i, func in enumerate(functions):
                    if i == selected_index:
                        # Highlight current option
                        print(f"{Back.WHITE}{Fore.BLACK}{func[0]}{Style.RESET_ALL}")
                    else:
                        print(func[0])
            except Exception:
                logging()

        while True:
            startMenu()
            key = readchar.readkey()

            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(functions)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(functions)
            elif key == readchar.key.ENTER:
                # Add Password is treated separately since it requires the mode variable to be passed
                # but does not get passed to performAction() because it does not need the password_list to be displayed
                # The mode variable needs to be explicitly defined here since later functions expect "Create"
                if functions[selected_index][0].split(' ', 1)[0] == "Create":
                    functions[selected_index][-1](user, mode="Create")
                # User Management and Migrate Database are also not passed to performAction() since
                # they do not require the passwords to be listed like Edit, Delete or Decrypt Password
                # .split(' ', 1)[0] extracts the first word of functions[selected_index][0] to compare against
                # These functions also do not need the mode variable to be passed
                elif functions[selected_index][0].split(' ', 1)[0] in ["User", "Migrate"]:
                    functions[selected_index][-1](user)
                # Sign Out and Quit do not require any arguments to be passed so are called separately
                # Check if selected index is within the last 2 items of
                # functions then execute last item in the selected tuple
                elif selected_index >= len(functions) - 2:
                    functions[selected_index][-1]()
                else:
                    # These items pass the mode argument to performAction() to display the password_list
                    performAction(user, mode=functions[selected_index][-1])
    except Exception:
        logging()


# Get func arg then perform action
# Feature argument is used to determine SQL query can be Sort or Search
# feature_variable argument provides the SQLquery with the user input
def performAction(user, mode, feature_variable=None, feature=None) -> None:
    try:
        # Define actions as (label, function)
        functions = [
            (updatePassword, "Edit"),
            (deletePassword, "Delete"),
            (displayPassword, "Decrypt")
        ]

        for func in functions:
            # Skip logic where func[-1] does not equal the current mode
            if func[-1] != mode:
                continue
            # Execute chosen function
            else:
                # Clear Terminal and print Logo
                logoScreen()

                if feature == None:
                    # Query the passwords table and insert all into passwords_list ordered by account name
                    passwords_list = sqlite.queryData(user, table="passwords")
                elif feature == "Search":
                    passwords_list = sqlite.queryData(user, table="passwords", category=feature_variable[0], text=feature_variable[1], sort_by=None)
                elif feature == "Sort":
                    passwords_list = sqlite.queryData(user, table="passwords", category=feature_variable[0], text=None, sort_by=feature_variable[1])

                # Check if passwords_list is empty
                if listNotEmpty(passwords_list):

                    selected_index = 0

                    while True:
                        # Display the table with navigation
                        displayTable(passwords_list, selected_index, table="passwords")

                        # User input via keyboard
                        key = readchar.readkey()

                        if key == readchar.key.UP:
                            selected_index = (selected_index - 1) % len(passwords_list)
                        elif key == readchar.key.DOWN:
                            selected_index = (selected_index + 1) % len(passwords_list)
                        elif key == readchar.key.CTRL_F:
                            searchPassword(user, mode)
                        elif key == readchar.key.CTRL_S:
                            sortPassword(user, mode)
                        elif key == readchar.key.ENTER:
                            # Execute func (func == i[0]) with required args
                            func[0](passwords_list[selected_index][0], passwords_list, selected_index, mode)
                            break
                        elif key == readchar.key.ESC:
                            start(user)
                            break
                else:
                    if enterContinue(enter_continue_statement=f"There are no passwords to {mode.lower()}") is True:
                        start(user)
    except Exception:
        logging()


# Password is encrypted then added to the encrypted passwords SQLite table
def addPassword(user, mode) -> None:
    try:
        # Clear Terminal and print Logo
        logoScreen()
        new_category = str(input("Category: "))
        new_account = str(input("Account: "))
        new_username = str(input("Username: "))
        new_password = str(input("Password: "))

        # Check if required fields are populated before proceeding
        # Returns True if both new_username and new_password were entered
        if new_username and new_password:
            save_password = encryptPassword(new_password)
            sqlite.insertData(user, new_category, new_account, new_username, save_password, session_password_key.decode())

            # Return to Start Menu or repeat
            # Success statement needs to slice first letter off done statement
            # Other functions incl edit and drecypt so deleteed is wrong
            tryAgain(user, mode, new_account, (done[0][1:]))
        else:
            if enterContinue(enter_continue_statement="Username and Password fields are required") is True:
                addPassword(user, mode)
    except Exception:
        logging()


# Update password
def updatePassword(user, passwords_list, index, mode) -> None:
    try:
        # Before updating the password we need to save the returned account and username for the update statement
        # Ran into errors when passing str(passwords_list[index][number]) directly in the SQLite update statement
        account = str(passwords_list[index][2])
        username = str(passwords_list[index][3])
        old_password = str(passwords_list[index][-3])

        replace_password = str(input("New Password: "))
        # Returns True if replace_password was entered
        if replace_password:
            save_password = encryptPassword(replace_password)
            sqlite.updateData(user, save_password, account, username, old_password, session_password_key.decode())

            # Return to Start Menu or repeat
            tryAgain(user, mode, (passwords_list[index][2]), (done[0]))
        else:
            if enterContinue(enter_continue_statement="New password was not entered") is True:
                updatePassword(user, passwords_list, index, mode)
    except Exception:
        logging()


# Delete password
def deletePassword(user, passwords_list, index, mode) -> None:
    try:
        # Before deleting the password we need to save the returned account and username for the delete statement
        account = str(passwords_list[index][2])
        username = str(passwords_list[index][3])
        old_password = str(passwords_list[index][-3])

        # Check if the user wants to delete the chosen password
        statement = (f"Are you sure you want to delete the password for {Fore.YELLOW}{passwords_list[index][2]}{Style.RESET_ALL} ?\n")
        if choice(statement, user, mode, password=None, confirm_delete=True, type="Password") == True:
            # Delete data from SQLite table
            sqlite.deleteData(user, account, username, old_password)
            # Return to Start Menu or repeat
            # Success statement needs to slice first letter off done statement
            # Other functions incl edit and drecypt so deleteed is wrong
            tryAgain(user, mode, (passwords_list[index][2]), (done[0][1:]))
        else:
            performAction(user, mode)
    except Exception:
        logging()


# Display password
def displayPassword(user, passwords_list, index, mode) -> None:
    try:
        # Before decrypting the password we need to save the returned Encryption Key for that record
        password_key = passwords_list[index][-2]
        password = passwords_list[index][-3]
        decrypted_password = decryptPassword(password_key, password)
        # Decrypt then return to Start Menu or repeat
        tryAgain((passwords_list[index][0]), mode, (passwords_list[index][2]), (done[0]), decrypted_password)
    except Exception:
        logging()


def searchPassword(user, mode) -> None:
    try:
        # Empty feature_variable incase it already has a value of somekind
        feature_variable = []

        options = [
            "Category",
            "Account",
            "Username"
            ]

        selected_index = 0

        while True:
            displayOptions(options, selected_index, display_statement=navigation_text)
            key = readchar.readkey()

            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(options)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(options)
            elif key == readchar.key.ENTER:
                # Add the selected Category to the feature_variable List
                search_category = options[selected_index]
                feature_variable.append(search_category.lower())
                break
            elif key == readchar.key.ESC:
                performAction(user, mode)
                break

        # Add the user input text to the feature_variable List
        search_text = input(f"\nSearch {search_category} for: ")
        feature_variable.append(search_text.lower())

        performAction(user, mode, feature_variable, feature="Search")
    except Exception:
        logging()


def sortPassword(user, mode) -> None:
    try:
        # Empty feature_variable incase it already has a value of somekind
        feature_variable = []

        options = [
            "Category",
            "Account",
            "Username"
            ]

        selected_index = 0

        while True:
            displayOptions(options, selected_index, display_statement=f"{navigation_text}\nSort By:\n")
            key = readchar.readkey()

            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(options)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(options)
            elif key == readchar.key.ENTER:
                # Add the selected Category to the feature_variable List
                sort_category = options[selected_index]
                feature_variable.append(sort_category.lower())
                break
            elif key == readchar.key.ESC:
                performAction(user, mode)
                break

        options = [
            "Ascending",
            "Descending"
            ]

        selected_index = 0

        while True:
            displayOptions(options, selected_index, display_statement=f"{navigation_text}\n Sort By {sort_category}:\n")
            key = readchar.readkey()

            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(options)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(options)
            elif key == readchar.key.ENTER:
                # Add the selected Category to the feature_variable List
                sort_by = options[selected_index]
                # Convert sort_by fromm Ascending to asc or Descending to desc
                feature_variable.append(sort_by.upper()[:-6])
                break
            elif key == readchar.key.ESC:
                performAction(user, mode)
                break

        performAction(user, mode, feature_variable, feature="Sort")
    except Exception:
        logging()


def userManagement(user) -> None:
    try:
        # Define actions as (label, function)
        functions = [
        ("Edit Master Password", updateMaster),
        ("Create New Master User", newMaster),
        ("Delete Master User", removeMaster),
        ("Main Menu", start),
        ("Quit", exit)
        ]

        # Extract the option labels for display
        options = [item[0] for item in functions]

        selected_index = 0

        while True:
            displayOptions(options, selected_index, display_statement=navigation_text)
            key = readchar.readkey()

            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(options)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(options)
            elif key == readchar.key.ENTER:
                # Quit does not take any arguments and cannot be passed the user variable
                # so needs to be called directly
                if selected_index == (len(functions)-1):
                    functions[selected_index][1]()
                else:
                    functions[selected_index][1](user)
    except Exception:
        logging()


# Create new master password
def newMaster(user=None) -> None:
    try:
        # First query the Users table to ensure the inputted user does not already exist
        master_users_list = sqlite.queryData(user=None, table="users")
        # Create an empty list of Master Users
        list_masters = []
        # Loop through SQL query and insert first field into intemediary list
        # to compare against provided new_master_user
        # SQLite3 Database has UNIQUE constraint on this feild but error will not be
        # obvious to the user until Logs are reviewed
        for i, master_user in enumerate(master_users_list):
            list_masters.append(master_user[0])

        # Clear Terminal and print Logo
        logoScreen()

        new_master_user = str(input("\nCreate new master user: "))
        # Returns True if new_master_user was entered
        if new_master_user:
            # Checks if new_master_user entered is not unique
            if new_master_user in list_masters:
                if enterContinue(enter_continue_statement="A Master User already exists with this name") is True:
                    # Try again and pass current user argument
                    # User is None if this is called when creating first Master User
                    newMaster(user)
        else:
            if enterContinue(enter_continue_statement="Master User cannot be empty.") is True: # FIX THIS - Accidentally catches wrong enter_continue_statement
                # Try again and pass current user argument
                # User is None if this is called when creating first Master User
                newMaster(user)

        new_master_password = str(input("Create new master password: "))
        # Check if the password is provided
        if new_master_password:
            save_password = encryptPassword(new_master_password)
            sqlite.insertUser(new_master_user, save_password, session_password_key.decode())
            # Go to Login screen after creating new Master User
            # Sign Out of current user and allow user to Sign In with new Master User or other
            if user is None:
                # enter_continue_statement is amended if user argument is None since this case
                # covers creating the first Master User
                enter_continue_statement=f"Master User {Fore.GREEN}{new_master_user}{Style.RESET_ALL} has been created"
            else:
                enter_continue_statement=f"Master User {Fore.GREEN}{new_master_user}{Style.RESET_ALL} has been created\n\nYou have been Signed Out of {user}"
            if enterContinue(enter_continue_statement) is True:
                splashScreen()
        else:
            if enterContinue(enter_continue_statement="Password cannot be empty.") is True:
                # Try again and pass current user argument
                # User is None if this is called when creating first Master User
                newMaster(user) 
    except Exception:
        logging()


# Create new master password
def updateMaster(user) -> None:
    try:
        logoScreen()
        new_master_password = str(input(f"\nEnter new master password for {user}: "))

        # Check if new_master_password was provided before proceeding
        # Returns True if new_master_password was entered
        if new_master_password:
            save_password = encryptPassword(new_master_password)
            sqlite.updateUserPassword(user, save_password, session_password_key.decode())
            if enterContinue(enter_continue_statement=f"Password updated for Master User {user}") is True:
                # Return to Log In screen
                splashScreen()
        else:
            if enterContinue(enter_continue_statement="No password was entered!") is True:
                updateMaster(user)
    except Exception:
        logging()


def removeMaster(user) -> None:
    try:
        # Query the users table and insert all into master_users_list
        master_users_list = sqlite.queryData(user=None, table="users")

        selected_index = 0

        while True:
            # Display the table with navigation
            displayTable(master_users_list, selected_index, table="users")

            # User input via keyboard
            key = readchar.readkey()

            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(master_users_list)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(master_users_list)
            elif key == readchar.key.ENTER:
                # Check if the user wants to delete the chosen Master User
                statement = (f"Are you sure you want to delete the Master User {Fore.YELLOW}{master_users_list[selected_index][0]}{Style.RESET_ALL} ?\n")
                if choice(statement, user, mode="Delete", password=None, confirm_delete=True, type="Master User") == True:
                    sqlite.deleteUser(user=master_users_list[selected_index][0])
                    if user == master_users_list[selected_index][0]:
                        if enterContinue(enter_continue_statement=f"Current User {Fore.YELLOW}{user}{Style.RESET_ALL} has been deleted") is True:
                            splashScreen()
                    else:
                        start(user)
            elif key == readchar.key.ESC:
                userManagement(user)
    except Exception:
        logging()


def migrateDatabase(user) -> None:
    try:
        # Define actions as (label, function)
        functions = [
        ("Export Database", exportDB),
        ("Import Database", importDB),
        ("Main Menu", start),
        ("Quit", exit)
        ]

        # Extract the option labels for display
        options = [item[0] for item in functions]

        selected_index = 0

        while True:
            displayOptions(options, selected_index, display_statement=navigation_text)
            key = readchar.readkey()

            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(options)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(options)
            elif key == readchar.key.ENTER:
                # Quit does not require user argument to be passed and needs to be called separately
                if selected_index == (len(functions)-1):
                    functions[selected_index][1]()
                else:
                    functions[selected_index][1](user)
    except Exception:
        logging()


# Exporting Database mostly uses CLI_Guard_SQL but requires text provided to the user
def exportDB(user) -> None:
    try:
        export_path = os.path.join(os.getcwd(), f"CLI_Guard_DB_Export_{today}.db")
        # Call SQLite3 function to export the database as {os.getcwd()}\CLI_Guard_DB_Export_{today}.db
        # Check if operation succeeded
        if sqlite.exportDatabase(export_path) is True:
            # Display File Path to Exported Database and allow user to return to Start Menu
            if enterContinue(enter_continue_statement=f"Database exported as {export_path}") is True:
                start(user)
        else:
            if enterContinue(enter_continue_statement="Database export failed") is True:
                migrateDatabase(user)
    except Exception:
        logging()

def importDB(user) -> None:
    try:
        # Initialise empty list of available_databases
        available_databases  = []

        # Loop through the files in the current directory
        for file in os.listdir(os.getcwd()):
            # If the file type is .db, append it to the available_databases list
            if file.endswith(".db"):
                # Remove file type and append as tuple to account for extended_list
                available_databases.append((file[:-3], ""))
        
        if listNotEmpty(available_databases):
            selected_index = 0

            while True:
                # Append more options to the table to allow user to enter file path manually
                extended_list = available_databases + [("Enter File Path Manually", importManually), ("Main Menu", start), ("Quit", exit)]

                # Display the table with navigation
                displayTable(extended_list, selected_index, table="databases")

                # User input via keyboard
                key = readchar.readkey()

                if key == readchar.key.UP:
                    selected_index = (selected_index - 1) % len(extended_list)
                elif key == readchar.key.DOWN:
                    selected_index = (selected_index + 1) % len(extended_list)
                elif key == readchar.key.ENTER:
                    # First check if selected_index is the last item in extended_list
                    # since Quit does not require any arguments to be passed and needs to be called separately
                    # This will be evaluated first before the next check of last 3 items
                    if selected_index >= len(extended_list) - 1:
                        extended_list[selected_index][-1]()
                    # Check if selected index is within the last 3 items of
                    # extended_list then execute last item in the selected tuple and pass user argument
                    elif selected_index >= len(extended_list) - 3:
                        extended_list[selected_index][-1](user)
                    else:
                        # Pass selected database and current directory to SQLite importDatabase function
                        import_path = os.path.join(os.getcwd(), f"{available_databases[selected_index][0]}.db")
                        importData(import_path)
        else:
            # Change this to allow user to enter file path manually
            statement = f"There are no databases in the current directory to import\n\nMove a database file to {os.getcwd()} and try again or enter the File Path manually\n"
            choice(statement, user, mode="Import")
    except Exception:
        logging()

# Import a database manually
def importManually(user) -> None:
    try:
        # Clear Terminal and print Logo
        logoScreen()
        import_path = str(input("\nEnter the full File Path including File Name of the database to be imported\n\nFile Path: "))

        if os.path.exists(import_path):
            if import_path.endswith(".db"):
                importData(user, import_path)
            else:
                if enterContinue(enter_continue_statement="File Path entered is not a database file") is True:
                    importDB(user)
        else:
            if enterContinue(enter_continue_statement=f"Could not find File Path entered\n{import_path} does not exist") is True:
                importDB(user)
    except Exception:
        logging()


# Logic to perform Database Import functions
def importData(user, import_path) -> None:
    try:
        # Query the Users table to compare against imported users
        existing_users = sqlite.queryData(user=None, table="users")
        # Create an empty list of existing Master Users
        existing_users_list =[]
        # Loop through SQL query and insert first field into
        # an intemediary list to compare against imported users
        for i, existing_user in enumerate(existing_users):
            existing_users_list.append(existing_user[0])

        # Query the imported Users table and insert all values of the imported users table into a list 
        imported_users_list = sqlite.importDatabase(import_path, table="users")
        # Create a empty list of decrypted Master Users
        decrypted_imported_users = []
        # Loop through the imported_users_list and add all values into a list
        # with the original password decrypted using the original encryption_key
        for i, imported_user in enumerate(imported_users_list):
            decrypted_imported_users.append(
                [
                    imported_users_list[i][0],
                    decryptPassword(encryption_key=imported_user[2],
                                    password=imported_user[1])
                ]
            )
        
        # Check if each imported Master User is unique and insert to Users table
        # with the original password encrypted using the current session_password_key
        # Master Users are handled differently here since only the user field is checked
        # for uniqueness while users passwords are checked for uniqueness across all fields
        for i, decrypted_user in enumerate(decrypted_imported_users):
            if decrypted_user[0] not in existing_users_list:
                sqlite.insertUser(
                    user=decrypted_user[0],
                    password=encryptPassword(decrypted_user[1]),
                    session_key=session_password_key.decode()
                )


        # Query the Passwords table to compare against imported passwords
        existing_passwords = sqlite.queryData(user=None, table="passwords")
        # Create an empty list of existing passwords
        existing_passwords_list = []
        # Loop through the imported_passwords_list and add all values into a list
        # with the original password decrypted using the original encryption_key
        for i, existing_password in enumerate(existing_passwords):
            existing_passwords_list.append(
                [
                    existing_password[0],
                    existing_password[1],
                    existing_password[2],
                    existing_password[3],
                    decryptPassword(encryption_key=existing_password[5],
                                    password=existing_password[4])
                ]
            )

        # Insert all values of the imported users table into a list 
        imported_passwords_list = sqlite.importDatabase(import_path, table="passwords")
        # Create a empty list of decrypted Master Users
        decrypted_imported_passwords = []
        # Loop through the queried data and append all values into the decrypted_imported_passwords list
        for i, imported_password in enumerate(imported_passwords_list):
            decrypted_imported_passwords.append(
                [
                    imported_password[0],
                    imported_password[1],
                    imported_password[2],
                    imported_password[3],
                    decryptPassword(encryption_key=imported_password[5],
                                    password=imported_password[4])
                ]
            )

        # Check if each imported password is unique and insert to Passwords table
        # with the original password encrypted using the current session_password_key
        for i, decrypted_password in enumerate(decrypted_imported_passwords):
            if i not in existing_passwords_list:
                sqlite.insertData(
                    user=decrypted_password[0],
                    category=decrypted_password[1],
                    account=decrypted_password[2],
                    username=decrypted_password[3],
                    password=encryptPassword(decrypted_password[4]),
                    session_key=session_password_key.decode()
                )
        
        logging(message=f"Successfully imported database from file path {import_path}")
        if enterContinue("Database imported successfully") is True:
            start(user)

    except Exception:
        logging()


def displayTable(list_table, selected_index,table) -> None:
    try:
        if table == "passwords":
            # Clear Terminal and print Logo with navigation_text and Search/Sort features
            logoScreen(logo_statement=(navigation_text + features))
        else:
            # Clear Terminal and print Logo with navigation_text
            logoScreen(logo_statement=navigation_text)

        # Create intermediary list to display data to Terminal with Tabulate
        tabulate_table = []
        place = 1
        
        if table == "passwords":
            for i in list_table:
                tabulate_table.append([place, i[1], i[2], i[3], i[-1]])
                place += 1
            # Print the headers
            print(tabulate([], headers=["Index", "Category", "Account", "Username", "Last Modified"], tablefmt="plain"))
        elif table == "users":
            for i in list_table:
                tabulate_table.append([i[0]])
                place += 1
            # Print the headers
            print(tabulate([], headers=["Select User"], tablefmt="plain")) 
        elif table == "databases":
            for i in list_table:
                tabulate_table.append([i[0]])
                place += 1
            # Print the headers
            print(tabulate([], headers=["Select Database to Import"], tablefmt="plain")) 
        
        # Display the table rows starting from the first row
        for i, row in enumerate(tabulate_table):
            if i == selected_index:
                # Highlight the current row
                print(Back.WHITE + Fore.BLACK + tabulate([row], headers=[], tablefmt="plain", maxcolwidths=[30, 50]) + Style.RESET_ALL)
            else:
                print(tabulate([row], headers=[], tablefmt="plain", maxcolwidths=[30, 50]))

        # Dump intermediary list after use
        tabulate_table = []
    except Exception:
        logging()


def displayOptions(options, selected_index, display_statement) -> None:
    try:
        # Clear Terminal and print Logo with display_statement
        logoScreen(logo_statement=display_statement)

        # Display the options with highlighted row
        for i, row in enumerate(options):
            if i == selected_index:
                # Highlight the current row
                print(Back.WHITE + Fore.BLACK + row + Style.RESET_ALL)
            else:
                print(row)
        return selected_index
    except Exception:
        logging()


# User chooses to perform the function again or return to Start
def tryAgain(user, mode, account, fixed_done, password=None) -> None:
    try:
        if mode == "Decrypt":
            statement = (f"\n{password}\n\n" + mode + fixed_done + f"{Fore.GREEN}{account}{Style.RESET_ALL}" + done[1])
            choice(statement, user, mode, password)
        else:
            statement = (mode + fixed_done + f"{Fore.GREEN}{account}{Style.RESET_ALL}" + done[1])
            choice(statement, user, mode)
    except Exception:
        logging()


# Handles Yes No choices
def choice(statement, user, mode=None, password=None, confirm_delete=None, type=None) -> None:
    try:
        selected_index = 0

        # Below functions defined here for actions that need arguments
        def copy() -> None:
            try:
                pyperclip.copy(password)
                updated_statement = (f"\n{password}\n\n"
                                    + "Password copied to clipboard" + done[1])
                choice(updated_statement, user, mode, password)
            except Exception:
                logging()

        def performAnother() -> None:
            try:
                if mode == "Create":
                    # Create Another Password cannot be passed to performAction()
                    # since it does not require the passwords_list to be displayed
                    addPassword(user, mode)
                else:
                    performAction(user, mode)
            except Exception:
                logging()

        def chooseAgain() -> bool:
            try:
                return False
            except Exception:
                logging()

        def confirm() -> bool:
            try:
                return True
            except Exception:
                logging()

        # Initialise list of available actions
        actions = []

        # Define actions as (label, function)
        # Extend the empty list of available actions with mode specific actions
        # list.extend is used to avoid issues where list.append expects a single argument
        # list.append would add the provided tuples as a single item
        if confirm_delete is True:
            actions.extend([(f"{mode} {type}", confirm), ("Choose Again", chooseAgain)])
        elif mode == "Decrypt":
            actions.extend([("Copy to Clipboard", copy), (f"{mode} Another Password", performAnother)])
        elif mode in ["Create", "Edit", "Delete"]:
            actions.extend([(f"{mode} Another Password", performAnother)])
        elif mode == "Import":
            actions.extend([("Enter File Path Manually", importManually)])
        
        # Main Menu and Quit are consistently the last 2 available actions for all cases
        actions.extend([("Main Menu", start), ("Quit", exit)])

        # Extract option labels for display
        options = [item[0] for item in actions]

        while True:
            displayOptions(options, selected_index, display_statement=(statement + navigation_text))
            key = readchar.readkey()

            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(options)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(options)
            elif key == readchar.key.ENTER:
                #  Start() and importManually() require the user argument to be passed
                if actions[selected_index][-1] in [start, importManually]:
                    actions[selected_index][-1](user)
                # confirm() and chooseAgain() were not being called correctly
                # and needed to be called separately to return the boolean
                elif actions[selected_index][-1] in [confirm, chooseAgain]:
                    returned_boolean = actions[selected_index][-1]()
                    return returned_boolean
                else:
                    # Call the corresponding function
                    actions[selected_index][-1]()
    except Exception:
        logging()



# Start CLI Guard in Terminal
if __name__ == "__main__":
    splashScreen()