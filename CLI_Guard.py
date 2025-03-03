# CLI Guard SQL
import  CLI_SQL.CLI_Guard_SQL as sqlite

# Tabulate is used to output list_passwords and list_master data to Terminal in grid format
from tabulate import tabulate

# OS is imported to send 'cls' to the Terminal between functions
from os import system

# PyperClip used to Copy to Clipboard
import pyperclip

# Readchar is used for Terminal navigation
import readchar

# Import PyGetWindow to get current window size
import pygetwindow as gw

# DateTime used when editing passwords or adding new passwords
from datetime import date, datetime, timedelta

today = date.today()
todays_time = datetime.now().strftime('%Y-%m-%d %H:%M')
tomorrow = date.today() + timedelta(1)

# Colour text and others
from colorama import init, Fore, Back, Style

# Initialize Colorama (autoreset restores default after print)
init(autoreset=True)

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



# Create empty list of encrypted passwords
list_passwords = []



# Formatting Terminal output
# Not all message-pieces should be kept in a list
# Overuse of lists for message-pieces makes creating messages confusing
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
       {Fore.BLUE}██████╗ ██╗      ██╗     ██████╗  ██╗   ██╗  █████╗  ██████╗  ██████╗{Fore.WHITE}
      {Fore.BLUE}██╔════╝ ██║      ██║    ██╔════╝  ██║   ██║ ██╔══██╗ ██╔══██╗ ██╔══██╗{Fore.WHITE}
      {Fore.LIGHTBLUE_EX}██║      ██║      ██║    ██║  ███╗ ██║   ██║ ███████║ ██████╔╝ ██║  ██║{Fore.WHITE}
      {Fore.LIGHTBLUE_EX}██║      ██║      ██║    ██║   ██║ ██║   ██║ ██╔══██║ ██╔══██╗ ██║  ██║{Fore.WHITE}
      {Fore.CYAN}╚██████╗ ███████╗ ██║    ╚██████╔╝ ╚██████╔╝ ██║  ██║ ██║  ██║ ██████╔╝{Fore.WHITE}
       {Fore.LIGHTCYAN_EX}╚═════╝ ╚══════╝ ╚═╝     ╚═════╝   ╚═════╝  ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═════╝ {Fore.WHITE}                     
"""


doing = "ing password..."
done = ["ed password for ", "...\n"]
empty_list = ["There are no passwords to ", "...\n"]
go_home = "Return to Start Menu?\n"
mode = ""
line = f"\n###################################################################################\n"
incorrect = "Incorrect password entered 3 times"
navigation = f"{Fore.CYAN}Use ↑ and ↓ to navigate\nPress Enter to select{Style.RESET_ALL}\n"
features = f"{Fore.CYAN}Return to Main Menu using ESC\nSearch using CTRL + F\nSort using CTRL + S{Style.RESET_ALL}\n"
# Initialise feature_variable as List to accept multiple arguments
feature_variable = []



# Maximize the terminal using pygetwindow
def maximizeTerminal():
    try:
        # Get all windows and filter by titles that match the criteria
        windows = gw.getAllWindows()
        
        for window in windows:
            # Check if the title is either 'Command Prompt' or contains '\cmd'
            if "Command Prompt" in window.title or "\\cmd" in window.title:
                window.maximize()
    except Exception as error:
        logging(error)


# Attempt Log In if user exists
def TerminalLogIn() -> None:
    try:
        # Maximize terminal window
        maximizeTerminal()
        # Clear Terminal then SPLASH
        system("cls")
        # Print CLI Guard Splash
        print(splash)
        # Query the users table and insert all into list_master
        list_master = sqlite.queryData(table = "users")
        # Check if list_master is empty
        if listNotEmpty(list_master):
            # Check if account is locked before logging in
            if accountLocked(list_master):
                print(f"Account locked until {tomorrow}\nExiting...")
                exit()
            else:
                # Proceed to Log In screen from Attempt Log In screen
                # Before decrypting the password we need to save the returned Encryption Key for that record
                # Make number of attempted passwords 0 from Attempt Log In screen
                logIn(user = list_master[0][0], attempt = 0, master_key = list_master[0][2], master_password = list_master[0][1])
        else:
            # Create a new master password if doesn't exist
            newMaster()
    except Exception as error:
        logging(error)


def accountLocked(list) -> bool:
    return str(list[0][-1]) == str(today)


def listNotEmpty(list) -> bool:
    return list != []


def fieldNotEmpty(*field) -> bool:
    return field != ''


# Log In screen to avoid splash everytime
def logIn(user, attempt, master_key, master_password) -> None:
    try:
        # 3 attempts to Log In before logging to log file and locking account for 1 day
        if attempt < 3:
            # Decrypt user password to compare with password entered
            decrypted_master_password = decryptPassword(master_key, master_password)
            attempted_password = str(input("Master password: "))
            if attempted_password == decrypted_master_password:
                # Need to fix this to check is user password = password saved to db for userID
                Start(user)
            else:
                # Clear Terminal and print Splash
                system("cls")
                print(splash)
                # Add attempt to attempts before returning to Log In screen
                attempt += 1
                print(f"{Fore.RED}{line}{Fore.WHITE}Incorrect password attempted")
                logIn(user, attempt, master_key, master_password)
        else:
            # Set last_locked to today on the users table
            sqlite.lockMaster(user, today)
            # Print exiting to screen
            print(f"{incorrect}\nExiting...")
            exit()
    except Exception as error:
        logging(error)


# Display Splash and Start Menu to CLI - User chooses function
def Start(user) -> None:
    try:
        # Clear Terminal
        system("cls")
        # Define function index, human-readable text, function name
        functions = [
            ("Create new password", "Add"),
            ("Edit a password", "Edit"),
            ("Delete a password", "Delete"),
            ("Display a password", "Decrypt"),
            ("Edit master password", "Master password"),
            ("Quit", "Quit")
        ]

        selected_index = 0

        def startMenu():
            system('cls')
            print(f"{splash}\n{navigation}")
            for i, func in enumerate(functions):
                if i == selected_index:
                    # Highlight current option
                    print(f"{Back.WHITE}{Fore.BLACK}{func[0]}{Style.RESET_ALL}")
                else:
                    print(func[0])

        while True:
            startMenu()
            key = readchar.readkey()

            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(functions)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(functions)
            elif key == readchar.key.ENTER:
                if functions[selected_index][-1] == "Quit":
                    exit()
                else:
                    performAction(user, mode = functions[selected_index][-1])
    except Exception as error:
        logging(error)


# Get func arg then perform action
# Feature argument is used to determine SQL query can be Sort or Search
# feature_variable argument provides the SQLquery with the user input
def performAction(user, mode, feature_variable=None, feature=None) -> None:
    try:
        # Clear Terminal
        system("cls")

        # Define function index and function name
        functions = [
            (updatePassword, "Edit"),
            (deletePassword, "Delete"),
            (displayPassword, "Decrypt")
        ]

        if mode == "Add":
            addPassword(user, mode)
        elif mode == "Master password":
            updateMaster(user)
        else:
            for func in functions:
                if func[-1] != mode:
                    continue
                # Execute chosen function
                else:
                    print(logo + line)

                    if feature == None:
                        # Query the passwords table and insert all into list_passwords ordered by account name
                        list_passwords = sqlite.queryData(table="passwords")
                    elif feature == "Search":
                        list_passwords = sqlite.queryData(table="passwords", category=feature_variable[0], text=feature_variable[1], sort_by=None)
                    elif feature == "Sort":
                        list_passwords = sqlite.queryData(table="passwords", category=feature_variable[0], text=None, sort_by=feature_variable[1])

                    # Check if list_passwords is empty
                    if listNotEmpty(list_passwords):

                        selected_index = 0  # Initialize the index for navigation

                        while True:
                            # Display the table with navigation
                            displayTable(list_passwords, selected_index)

                            # User input via keyboard
                            key = readchar.readkey()

                            if key == readchar.key.UP:
                                selected_index = (selected_index - 1) % len(list_passwords)
                            elif key == readchar.key.DOWN:
                                selected_index = (selected_index + 1) % len(list_passwords)
                            elif key == readchar.key.CTRL_F:
                                searchPassword(user, mode)
                            elif key == readchar.key.CTRL_S:
                                sortPassword(user, mode)
                            elif key == readchar.key.ENTER:
                                # Execute func (func == i[0]) with required args
                                func[0](list_passwords[selected_index][0], list_passwords, selected_index, mode)
                                break
                            elif key == readchar.key.ESC:
                                Start(user)
                                break
                    else:
                        empty(user, mode)
    except Exception as error:
        logging(error)


# Password is encrypted then added to the encrypted passwords SQLite table
def addPassword(user, mode) -> None:
    try:
        print( logo + line )
        new_category = str(input("Category: "))
        new_account = str(input("Account: "))
        new_username = str(input("Username: "))
        new_password = str(input("Password: "))

        # Check all fields are populated before proceeding
        if fieldNotEmpty(new_category, new_account, new_username, new_password):
            print(mode + doing)
            save_password = encryptPassword(new_password)
            sqlite.insertData(user, new_category, new_account, new_username, save_password, session_password_key.decode(), today)

            # Return to Start Menu or repeat
            tryAgain( user, mode, new_account, (done[0]))
        else:
            print("All fields are required")
            addPassword(user)
    except Exception as error:
        logging(error)


# Update password
def updatePassword(user, list_passwords, index, mode) -> None:
    try:
        # Before updating the password we need to save the returned account and username for the update statement
        # Ran into errors when using list_passwords[index][1 or 0] directly in the SQLite update statement
        account = str(list_passwords[index][2])
        username = str(list_passwords[index][3])
        old_password = str(list_passwords[index][-3])

        replace_password = str(input("New Password: "))
        if fieldNotEmpty(replace_password):
            print(mode + doing)
            save_password = encryptPassword(replace_password)
            sqlite.updateData(save_password, account, username, old_password, session_password_key.decode(), today)

            # Return to Start Menu or repeat
            tryAgain(user, mode, (list_passwords[index][2]), (done[0]))
        else:
            print("New password was not entered")
            # Return to Start Menu or repeat
            tryAgain(user, mode, (list_passwords[index][2]), (done[0]))
    except Exception as error:
        logging(error)


# Delete password
def deletePassword(user, list_passwords, index, mode) -> None:
    try:
        # Before deleting the password we need to save the returned account and username for the delete statement
        account = str(list_passwords[index][2])
        username = str(list_passwords[index][3])
        old_password = str(list_passwords[index][-3])

        # Check if the user wants to delete the chosen password
        statement = (f"{Fore.YELLOW}{line}{Fore.WHITE}Are you sure you want to delete the password for {Fore.YELLOW}{list_passwords[index][2]}{Fore.WHITE} ?")
        if choice( statement, user, mode, password=None, confirm_delete=True ) == True:
            # Success statement needs to slice first letter off mode
            print(mode[:-1] + doing)
            # Delete data from SQLite table
            sqlite.deleteData(user, account, username, old_password)
            # Return to Start Menu or repeat
            # Success statement needs to slice first letter off mode
            # Other functions incl edit, add, drecypted so deleteed is wrong
            tryAgain(user, mode, (list_passwords[index][2]), (done[0][1:]))
        else:
            performAction(user, mode)
    except Exception as error:
        logging(error)


# Display password
def displayPassword(user, list_passwords, index, mode) -> None:
    try:
        # Before decrypting the password we need to save the returned Encryption Key for that record
        password_key = list_passwords[index][-2]
        password = list_passwords[index][-3]
        decrypted_password = decryptPassword(password_key, password)
        print(mode + doing)
        # Decrypt then return to Start Menu or repeat
        tryAgain((list_passwords[index][0]), mode, (list_passwords[index][2]), (done[0]), decrypted_password)
    except Exception as error:
        logging(error)


def displayTable(list_passwords, selected_index):
    try:
        system('cls')
        print( logo + line + "\n" + navigation + features )

        # Create intermediary list to display data to Terminal with Tabulate
        password_table = []
        place = 1
        for i in list_passwords:
            password_table.append([place, i[1], i[2], i[3], i[-3], i[-1]])
            place += 1

        # Print the headers
        print(tabulate([], headers=["Index", "Category", "Account", "Username", "Password", "Last Modified"], tablefmt="plain"))

        # Display the table rows starting from the first row
        for i, row in enumerate(password_table):
            if i == selected_index:
                # Highlight the current row
                print(Back.WHITE + Fore.BLACK + tabulate([row], headers=[], tablefmt="plain") + Style.RESET_ALL)
            else:
                print(tabulate([row], headers=[], tablefmt="plain"))

        # Dump intermediary list after use
        password_table = []
    except Exception as error:
        logging(error)


def searchPassword(user, mode):
    try:
        # Empty feature_variable incase it already has a value of somekind
        feature_variable = []

        data = [
            "Category",
            "Account",
            "Username"
            ]

        selected_index = 0

        def displayOptions():
            system('cls')
            print( navigation )

            # Display the options with highlighted row
            for i, row in enumerate(data):
                if i == selected_index:
                    # Highlight the current row
                    print(Back.WHITE + Fore.BLACK + row + Style.RESET_ALL)
                else:
                    print(row)

        while True:
            displayOptions()
            key = readchar.readkey()

            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(data)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(data)
            elif key == readchar.key.ENTER:
                # Add the selected Category to the feature_variable List
                search_category = data[selected_index]
                feature_variable.append(search_category.lower())
                break
            elif key == readchar.key.ESC:
                performAction(user, mode)
                break

        # Add the user input text to the feature_variable List
        search_text = input(f"\nSearch {search_category} for: ")
        feature_variable.append(search_text.lower())

        performAction(user, mode, feature_variable, feature="Search")
    except Exception as error:
        logging(error)


def sortPassword(user, mode):
    try:
        # Empty feature_variable incase it already has a value of somekind
        feature_variable = []

        data = [
            "Category",
            "Account",
            "Username"
            ]

        selected_index = 0

        def displayOptions():
            system('cls')
            print(f"{navigation}\n Sort By:\n")

            # Display the options with highlighted row
            for i, row in enumerate(data):
                if i == selected_index:
                    # Highlight the current row
                    print(Back.WHITE + Fore.BLACK + row + Style.RESET_ALL)
                else:
                    print(row)

        while True:
            displayOptions()
            key = readchar.readkey()

            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(data)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(data)
            elif key == readchar.key.ENTER:
                # Add the selected Category to the feature_variable List
                sort_category = data[selected_index]
                feature_variable.append(sort_category.lower())
                break
            elif key == readchar.key.ESC:
                performAction(user, mode)
                break

        data = [
            "Ascending",
            "Descending"
            ]

        selected_index = 0

        def displayOptions():
            system('cls')
            print(f"{navigation}\n Sort By {sort_category}:\n")

            # Display the options with highlighted row
            for i, row in enumerate(data):
                if i == selected_index:
                    # Highlight the current row
                    print(Back.WHITE + Fore.BLACK + row + Style.RESET_ALL)
                else:
                    print(row)

        while True:
            displayOptions()
            key = readchar.readkey()

            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(data)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(data)
            elif key == readchar.key.ENTER:
                # Add the selected Category to the feature_variable List
                sort_by = data[selected_index]
                # Convert sort_by fromm Ascending to asc or Descending to desc
                feature_variable.append(sort_by.upper()[:-6])
                break
            elif key == readchar.key.ESC:
                performAction(user, mode)
                break

        performAction(user, mode, feature_variable, feature="Sort")
    except Exception as error:
        logging(error)


# Create new master password
def newMaster() -> None:
    try:
        new_master_user = str(input("Create new master user: "))
        new_master_password = str(input("Create new master password: "))

        # Check all fields are populated before proceeding
        if fieldNotEmpty(new_master_user, new_master_password):
            print("Adding new master password...")
            save_password = encryptPassword(new_master_password)
            sqlite.insertMaster(new_master_user, save_password, session_password_key.decode(), today)
            # Return to Log In screen
            TerminalLogIn()
        else:
            print("1 or more required fields is missing!")
            newMaster()
    except Exception as error:
        logging(error)


# Create new master password
def updateMaster(user) -> None:
    try:
        print( logo + line )
        new_master_password = str(input("Enter new master password: "))

        # Check all fields are populated before proceeding
        if fieldNotEmpty(new_master_password):
            print("Editing master password...")
            save_password = encryptPassword(new_master_password)
            sqlite.updateMasterPassword(user, save_password, session_password_key.decode(), today)
            # Return to Log In screen
            TerminalLogIn()
        else:
            print("No password was entered!")
            updateMaster(user)
    except Exception as error:
        logging(error)


# The list_passwords list is empty - user chooses to return to Start or Exit
def empty(user, mode) -> None:
    try:
        statement =  ( empty_list[0] + mode.lower() + empty_list[1] + go_home )
        choice(statement, user, mode=0)
    except Exception as error:
        logging(error)


# User chooses to perform the function again or return to Start
# Ran into issues using the choice function because this calls the extra argument of func
def tryAgain( user, mode, account, fixed_done, password=None) -> None:
    try:
        if mode == "Decrypt":
            statement = ( f"\n{password}\n{Fore.GREEN}{line}{Fore.WHITE}" + mode + fixed_done + f"{Fore.GREEN}{account}{Fore.WHITE}" + done[1] )
            choice(statement, user, mode, password)
        else:
            statement = ( f"{Fore.GREEN}{line}{Fore.WHITE}" + mode + fixed_done + f"{Fore.GREEN}{account}{Fore.WHITE}" + done[1] )
            choice(statement, user, mode)
    except Exception as error:
        logging(error)


# Handles Yes No choices
def choice(statement, user, mode, password=None, confirm_delete=None) -> None:
    try:
        selected_index = 0
        
        if confirm_delete:
            options = [
                f"{mode} Password",
                "Choose Again",
                "Main Menu",
                "Quit"
                ]   
        elif mode == 0:
            options = [
                "Main Menu",
                "Quit"
                ]
        elif mode == "Decrypt":
            options = [
                "Copy to Clipboard",
                f"{mode} Another Password",
                "Main Menu",
                "Quit"
                ]
        else:
            options = [
                f"{mode} Another Password",
                "Main Menu",
                "Quit"
                ]

        def displayOptions():
            system('cls')
            print(f"{logo}\n{statement}\n{navigation}")
            for i, option in enumerate(options):
                if i == selected_index:
                    # Highlight current option
                    print(f"{Back.WHITE}{Fore.BLACK}{option}{Style.RESET_ALL}")
                else:
                    print(option)

        while True:
            displayOptions()
            key = readchar.readkey()

            if key == readchar.key.UP:
                selected_index = (selected_index - 1) % len(options)
            elif key == readchar.key.DOWN:
                selected_index = (selected_index + 1) % len(options)
            elif key == readchar.key.ENTER:
                if options[selected_index] == f"{mode} Password":
                    return True
                elif options[selected_index] == "Choose Again":
                    return False
                elif options[selected_index] == "Copy to Clipboard":
                    pyperclip.copy(password)
                    statement = ( f"\n{password}\n{Fore.GREEN}{line}{Fore.WHITE}" + "Password copied to clipboard" + done[1] )
                    choice(statement, user, mode, password)
                elif options[selected_index] == f"{mode} Another Password":
                    # To tryAgain we need to pass func variable as an argument when calling func variable
                    # Because each function expects a func argument so it can call tryAgain() if needed
                    performAction(user, mode)
                elif options[selected_index] == "Main Menu":
                    Start(user)
                elif options[selected_index] ==  "Quit":
                    print("Exiting...")
                    exit()
    except Exception as error:
        logging(error)


# Encrypt
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
    except Exception as error:
        logging(error)


# Decrypt
def decryptPassword(encryption_key, password) -> str:
    try:
        # Decrypted password needs to be saved to its own variable
        # We use Fernet(password_key) here instead of fernet variable to
        # Decrypt with the relevant records Encryption Key
        decrypted_password = Fernet(encryption_key).decrypt(password)
        # Remember to DECODE the new variable to convert from BITS datatype to STRING
        # This removes the leading b value changing b'variable' to 'variable'
        return decrypted_password.decode()
    except Exception as error:
        logging(error)


# Write to Log file
def logging(message):
    f = open(".\\Logs.txt", "a")
    f.write(f"[{todays_time}] {message}\n")
    f.close()


# Start CLI Guard in Terminal
if __name__ == "__main__":
    TerminalLogIn()