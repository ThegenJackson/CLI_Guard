# CLI Guard SQL
import  CLI_SQL.CLI_Guard_SQL as sqlite

# Tabulate is used to output passwords_list and master_users_list data to Terminal in grid format
from tabulate import tabulate

# Import OS library
import os

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
empty_list = ["There are no passwords to ", "...\n"]
go_home = "Return to Start Menu?\n"
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
def logging(message=None):
    with open(".\\Logs.txt", "a") as file:
        #  Handles Traceback since no message argument is passed
        if message is None:
            # traceback.format_exc() function works without explicitly passing an error
            # because it captures the most recent exception from the current context
            file.write(f"[{todays_time}] Traceback: {traceback.format_exc()}\n")
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


# The passwords_list is empty - user chooses to return to Start or Exit
def empty(user, mode) -> None:
    try:
        statement = (empty_list[0] + mode.lower() + empty_list[1] + go_home)
        choice(statement, user, mode=0)
    except Exception:
        logging()


# Clear Terminal and print Logo
# Avoids multiple lines of code each time a screen clear and logo print are required
# Not all calls to printLogo require a statement
# and when a statement is not provided "None" is printed to screen
def printLogo(logo_statement=None):
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
def enterContinue(enter_continue_statement):
    try:
        # Don't print Try Again message if creating Master User for first time
        # Match enter_continue_statement on second word instead of full text
        if enter_continue_statement.split(' ', 2)[1] == "Master":
            continue_action = "create new Mater User"
        # Don't print Try Again or Create New Mater
        # if calling enterContinue() from a Database Migration function
        # Match enter_continue_statement on second word instead of full text
        elif enter_continue_statement.split(' ', 2)[1] == "exported":
            # String "Return to Start Menu?" is predefined
            # but needs first character lowercase and last character removed
            continue_action = (go_home[0].lower() + go_home[1:])[:-2]
        else:
            continue_action = "try again"

        printLogo(logo_statement=f"\n{enter_continue_statement}\n\nPress Enter to {continue_action}")
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
def maximizeTerminal():
    try:
        # Get all windows and filter by titles that match the criteria
        windows = gw.getAllWindows()
        
        for window in windows:
            # Check if the title is either "Command Prompt" or contains "\cmd"
            if "Command Prompt" in window.title or "\\cmd" in window.title:
                window.maximize()
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

        def dotAnimation():
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


def login():
    try:
        # Clear Terminal and print Logo
        printLogo()
        # Query the users table and insert all into master_users_list
        master_users_list = sqlite.queryData(user=None, table="users")
        # Check if master_users_list is empty
        if listNotEmpty(master_users_list):
            selected_index = 0

            while True:
                # Append "Create New Master User" option to the table to 
                # allow user to create a new Master User directly from login screen
                extended_list = master_users_list + [("Create New Master User", "", ""), ("Quit", "", "")]

                # Display the table with navigation
                displayTable(extended_list, selected_index, table="users")

                # User input via keyboard
                key = readchar.readkey()

                if key == readchar.key.UP:
                    selected_index = (selected_index - 1) % len(extended_list)
                elif key == readchar.key.DOWN:
                    selected_index = (selected_index + 1) % len(extended_list)
                elif key == readchar.key.ENTER:
                    if selected_index == (len(extended_list)-2):
                        newMaster()
                    elif selected_index == (len(extended_list)-1):
                        exit()
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
                    printLogo()
                    # Add attempt to attempts before returning to Log In screen
                    attempt += 1
                    print(f"{Fore.RED}Incorrect password attempted{Style.RESET_ALL}")
                    attemptLogin(user, attempt, master_key, master_password)
            else:
                if enterContinue(enter_continue_statement=f"{Fore.RED}No password was entered{Style.RESET_ALL}") is True:
                    attemptLogin(user, attempt, master_key, master_password)
        else:
            # Set last_locked to today on the users table
            sqlite.lockMaster(user)
            # Write to Log file
            logging(message=f"Incorrect password entered 3 times for Master User {user}\nAccount {user} locked until {tomorrow}")
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
            ("Create new password", "Add"),
            ("Edit a password", "Edit"),
            ("Delete a password", "Delete"),
            ("Display a password", "Decrypt"),
            ("User Management", "Users"),
            ("Migrate Database", "Migrate"),
            ("Sign Out", "Sign Out"),
            ("Quit", "Quit")
        ]

        selected_index = 0

        def startMenu():
            try:
                # Clear Terminal and print Logo and navigation_text
                printLogo(logo_statement=navigation_text)
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
                # Sign Out and Quit do not require any arguments to be passed so are called separately
                if selected_index == (len(functions) -2):
                    login()
                elif selected_index == (len(functions) -1):
                    exit()
                else:
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

        # Add Password, User Management and Migrate Database are treated separately since they do not require
        # the passwords to be listed like Edit, Delete or Decrypt Password but they still require an argument to be passed
        # so they are not called from Start screen
        if mode == "Add":
            addPassword(user, mode)
        elif mode == "Users":
            userManagement(user)
        elif mode == "Migrate":
            migrateDatabase(user)
        else:
            for func in functions:
                if func[-1] != mode:
                    continue
                # Execute chosen function
                else:
                    # Clear Terminal and print Logo
                    printLogo()

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
                        empty(user, mode)
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
                # Exit does not take any arguments and cannot be passed the user variable
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
        # Loop through SQL query and insert first field into intemediary list
        # to compare against provided new_master_user
        # SQLite3 Database has UNIQUE constraint on this feild but error will not be
        # obvious to the user until Logs are reviewed
        list_masters = [user[0] for user in master_users_list]

        # Clear Terminal and print Logo
        printLogo()

        new_master_user = str(input("\nCreate new master user: "))
        # Returns True if new_master_user was entered
        if new_master_user:
            # Checks if new_master_user entered is not unique
            if new_master_user in list_masters:
                if enterContinue(enter_continue_statement="A Master User already exists with this name") is True:
                    newMaster()
        else:
            if enterContinue(enter_continue_statement="Master User cannot be empty.") is True:
                newMaster()

        new_master_password = str(input("Create new master password: "))
        # Check if the password is provided
        if new_master_password:
            save_password = encryptPassword(new_master_password)
            sqlite.insertMaster(new_master_user, save_password, session_password_key.decode())
            # Go to Start screen after creating new Master User
            # Handles issue where user variable is not passed to later functions
            if user is None:
                start(user=new_master_password)
            else:
                start(user)
        else:
            if enterContinue(enter_continue_statement="Password cannot be empty.") is True:
                newMaster(user) 
    except Exception:
        logging()


# Create new master password
def updateMaster(user) -> None:
    try:
        printLogo()
        new_master_password = str(input(f"\nEnter new master password for {user}: "))

        # Check if new_master_password was provided before proceeding
        # Returns True if new_master_password was entered
        if new_master_password:
            save_password = encryptPassword(new_master_password)
            sqlite.updateMasterPassword(user, save_password, session_password_key.decode())
            # Return to Log In screen
            splashScreen()
        else:
            if enterContinue(enter_continue_statement="No password was entered!") is True:
                updateMaster(user)
    except Exception:
        logging()


def removeMaster(user) -> None:
    try:
        # Clear Terminal and print Logo
        printLogo()

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
                    sqlite.deleteMaster(user=master_users_list[selected_index][0])
                    if user == master_users_list[selected_index][0]:
                        splashScreen()
                    else:
                        start(user)
            elif key == readchar.key.ESC:
                userManagement(user)
    except Exception:
        logging()


# Password is encrypted then added to the encrypted passwords SQLite table
def addPassword(user, mode) -> None:
    try:
        # Clear Terminal and print Logo
        printLogo()
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
            tryAgain(user, mode, new_account, (done[0]))
        else:
            if enterContinue(enter_continue_statement="Username and Password fields are required") is True:
                addPassword(user, mode)
    except Exception:
        logging()


# Update password
def updatePassword(user, passwords_list, index, mode) -> None:
    try:
        # Before updating the password we need to save the returned account and username for the update statement
        # Ran into errors when using passwords_list[index][1 or 0] directly in the SQLite update statement
        account = str(passwords_list[index][2])
        username = str(passwords_list[index][3])
        old_password = str(passwords_list[index][-3])

        replace_password = str(input("New Password: "))
        # Returns True if replace_password was entered
        if replace_password:
            save_password = encryptPassword(replace_password)
            sqlite.updateData(save_password, account, username, old_password, session_password_key.decode())

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
            # Success statement needs to slice first letter off mode
            # Other functions incl edit, add, drecypted so deleteed is wrong
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


def displayTable(list_table, selected_index, table):
    try:
        if table == "passwords":
            # Clear Terminal and print Logo with navigation_text and features
            printLogo(logo_statement=(navigation_text + features))
        elif table == "users":
            # Clear Terminal and print Logo with navigation_text
            printLogo(logo_statement=navigation_text)

        # Create intermediary list to display data to Terminal with Tabulate
        tabulate_table = []
        place = 1
        
        if table == "passwords":
            for i in list_table:
                tabulate_table.append([place, i[1], i[2], i[3], i[-3], i[-1]])
                place += 1
            # Print the headers
            print(tabulate([], headers=["Index", "Category", "Account", "Username", "Password", "Last Modified"], tablefmt="plain"))
        elif table == "users":
            for i in list_table:
                tabulate_table.append([i[0]])
                place += 1
            # Print the headers
            print(tabulate([], headers=["Select User"], tablefmt="plain")) 
        
        # Display the table rows starting from the first row
        for i, row in enumerate(tabulate_table):
            if i == selected_index:
                # Highlight the current row
                print(Back.WHITE + Fore.BLACK + tabulate([row], headers=[], tablefmt="plain") + Style.RESET_ALL)
            else:
                print(tabulate([row], headers=[], tablefmt="plain"))

        # Dump intermediary list after use
        tabulate_table = []
    except Exception:
        logging()


def displayOptions(options, selected_index, display_statement):
    try:
        # Clear Terminal and print Logo with display_statement
        printLogo(logo_statement=display_statement)

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


def searchPassword(user, mode):
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


def sortPassword(user, mode):
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


# User chooses to perform the function again or return to Start
# Ran into issues using the choice function because this calls the extra argument of func
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
        def copy():
            try:
                pyperclip.copy(password)
                updated_statement = (f"\n{password}\n\n"
                                    + "Password copied to clipboard" + done[1])
                choice(updated_statement, user, mode, password)
            except Exception:
                logging()

        def performAnother():
            try:
                performAction(user, mode)
            except Exception:
                logging()

        def mainMenu():
            try:
                start(user)
            except Exception:
                logging()

        def chooseAgain():
            try:
                return False
            except Exception:
                logging()

        def confirm():
            try:
                return True
            except Exception:
                logging()

        def exitApp():
            try:
                print("Exiting...")
                exit()
            except Exception:
                logging()

        # Define actions as (label, function)
        if confirm_delete:
            actions = [
                (f"{mode} {type}", confirm),
                ("Choose Again", chooseAgain),
                ("Main Menu", mainMenu),
                ("Quit", exitApp)
            ]
        elif mode == 0:
            actions = [
                ("Main Menu", mainMenu),
                ("Quit", exitApp)
            ]
        elif mode == "Decrypt":
            actions = [
                ("Copy to Clipboard", copy),
                (f"{mode} Another Password", performAnother),
                ("Main Menu", mainMenu),
                ("Quit", exitApp)
            ]
        else:
            actions = [
                (f"{mode} Another Password", performAnother),
                ("Main Menu", mainMenu),
                ("Quit", exitApp)
            ]

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
                # Call the corresponding function
                return actions[selected_index][1]()
    except Exception:
        logging()


def migrateDatabase(user) -> None:
    try:
        # Define actions as (label, function)
        functions = [
        ("Export Database", exportDB),
        ("Import Database", sqlite.importDatabase),
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
                # Returning to Start screen required user argument and needs to be called separately
                if selected_index == (len(functions)-2):
                    functions[selected_index][1](user)
                else:
                    functions[selected_index][1]()
    except Exception:
        logging()


# Exporting Database mostly uses CLI_Guard_SQL but requires text provided to the user
def exportDB():
    try:
        export_path = f"{os.getcwd()}\\CLI_Guard_DB_Export_{today}.db"
        # Call SQLite3 function to export the database as {os.getcwd()}\CLI_Guard_DB_Export_{today}.db
        sqlite.exportDatabase(export_path)
        # Display File Path to Exported Database and allow user to return to Start Menu
        enterContinue(enter_continue_statement=f"Database exported as {export_path}")
    except Exception:
        logging()


# Start CLI Guard in Terminal
if __name__ == "__main__":
    splashScreen()