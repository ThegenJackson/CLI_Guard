# CLI Guard SQL
import  CLI_SQL.CLI_Guard_SQL as sqlite

# Tabulate is used to output list_pw and list_master data to Terminal in grid format
from tabulate import tabulate

# OS is imported to send 'cls' to the Terminal between functions
from os import system

# Readchar is used for Terminal navigation
import readchar

# Import PyGetWindow to get current window size
import pygetwindow as gw

# DateTime used when editing passwords or adding new passwords
from datetime import date, datetime, timedelta

today = date.today()
todaysTime = datetime.now().strftime('%Y-%m-%d %H:%M')
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
key = Fernet.generate_key()
fernet = Fernet(key)
session_pw_key = key



# Create empty list of encrypted passwords
list_pw = []



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
go_back = "Return to Start Menu?\n"
mode = ""
line = f"\n###################################################################################\n"
incorrect = "Incorrect password entered 3 times"
navigation = f"{Fore.CYAN}Use ↑ and ↓ to navigate. Press Enter to select.{Style.RESET_ALL}\n"
features = f"{Fore.CYAN}Search using CTRL + F or Sort using CTRL + S{Style.RESET_ALL}\n"
# Initialise FeatureVariable as List to accept multiple arguments
featureVariable = []


# Maximize the terminal using pygetwindow
def maximize_terminal():
    # Get all windows and filter by titles that match the criteria
    windows = gw.getAllWindows()
    
    for window in windows:
        # Check if the title is either 'Command Prompt' or contains '\cmd'
        if "Command Prompt" in window.title or "\\cmd" in window.title:
            window.maximize()

# Attempt Log In if user exists
def TerminalLogIn() -> None:
    # Maximize terminal window
    maximize_terminal()
    # Clear Terminal then SPLASH
    system("cls")
    # Print CLI Guard Splash
    print(splash)
    # Query the users table and insert all into list_master
    list_master = sqlite.query_data(table = "users")
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
            logIn(user = list_master[0][0], attempt = 0, master_key = list_master[0][2], master_pw = list_master[0][1])
    else:
        # Create a new master password if doesn't exist
        new_Master()


def accountLocked(list) -> bool:
    return str(list[0][-1]) == str(today)


def listNotEmpty(list) -> bool:
    return list != []


def fieldNotEmpty(*field) -> bool:
    return field != ''


# Log In screen to avoid splash everytime
def logIn(user, attempt, master_key, master_pw) -> None:
    # 3 attempts to Log In before logging to log file and locking account for 1 day
    if attempt < 3:
        # Decrypt user password to compare with password entered
        decrypted_master_pw = decrypt_pw(master_key, master_pw)
        attempted_pw = str(input("Master password: "))
        if attempted_pw == decrypted_master_pw:
            # Need to fix this to check is user password = pw saved to db for userID
            Start(user)
        else:
            # Clear Terminal and print Splash
            system("cls")
            print(splash)
            # Add attempt to attempts before returning to Log In screen
            attempt += 1
            print(f"{Fore.RED}{line}{Fore.WHITE}Incorrect password attempted")
            logIn(user, attempt, master_key, master_pw)
    else:
        #  Write to log file
        logging(message = f"{incorrect}\n[{todaysTime}] Account locked until {tomorrow}")
        # Set last_locked to today on the users table
        sqlite.lock_master(user, today)
        # Print exiting to screen
        print(f"{incorrect}\nExiting...")
        exit()


# Display Splash and Start Menu to CLI - User chooses function
def Start(user) -> None:
    # Clear Terminal
    system("cls")
    # Define function index, human-readable text, function name
    funcs = [
        ("Create new password", "Add"),
        ("Edit a password", "Edit"),
        ("Delete a password", "Delete"),
        ("Display a password", "Decrypt"),
        ("Edit master password", "Master password"),
        ("Quit", "Quit")
    ]

    selected_index = 0

    def start_menu():
        system('cls')
        print(f"{splash}\n{navigation}")
        for i, func in enumerate(funcs):
            if i == selected_index:
                # Highlight current option
                print(f"{Back.WHITE}{Fore.BLACK}{func[0]}{Style.RESET_ALL}")
            else:
                print(func[0])

    while True:
        start_menu()
        key = readchar.readkey()

        if key == readchar.key.UP:
            selected_index = (selected_index - 1) % len(funcs)
        elif key == readchar.key.DOWN:
            selected_index = (selected_index + 1) % len(funcs)
        elif key == readchar.key.ENTER:
            if funcs[selected_index][-1] == "Quit":
                exit()
            else:
                do_action(user, mode = funcs[selected_index][-1])


# Get func arg then perform action
# Feature argument is used to determine SQL query can be Sort or Search
# FeatureVariable argument provides the SQLquery with the user input
def do_action(user, mode, featureVariable=None, feature=None) -> None:
    # Clear Terminal
    system("cls")

    # Define function index and function name
    funcs = [
        (update_pw, "Edit"),
        (delete_pw, "Delete"),
        (display_pw, "Decrypt")
    ]

    if mode == "Add":
        add_pw(user, mode)
    elif mode == "Master password":
        update_Master(user)
    else:
        for func in funcs:
            if func[-1] != mode:
                continue
            # Execute chosen function
            else:
                print(logo + line)

                if feature == None:
                    # Query the passwords table and insert all into list_pw ordered by account name
                    list_pw = sqlite.query_data(table="passwords")
                elif feature == "Search":
                    list_pw = sqlite.query_data(table="passwords", category=featureVariable[0], text=featureVariable[1], sortby=None)
                elif feature == "Sort":
                    list_pw = sqlite.query_data(table="passwords", category=featureVariable[0], text=None, sortby=featureVariable[1])

                # Check if list_pw is empty
                if listNotEmpty(list_pw):

                    selected_index = 0  # Initialize the index for navigation

                    while True:
                        # Display the table with navigation
                        display_table(list_pw, selected_index)

                        # User input via keyboard
                        key = readchar.readkey()

                        if key == readchar.key.UP:
                            selected_index = (selected_index - 1) % len(list_pw)
                        elif key == readchar.key.DOWN:
                            selected_index = (selected_index + 1) % len(list_pw)
                        elif key == readchar.key.CTRL_F:
                            search_pw(user, mode)
                        elif key == readchar.key.CTRL_S:
                            sort_pw(user, mode)
                        elif key == readchar.key.ENTER:
                            # Execute func (func == i[0]) with required args
                            func[0](list_pw[selected_index][0], list_pw, selected_index, mode)
                            break
                        elif key == readchar.key.ESC:
                            Start(user)
                            break
                else:
                    empty(user, mode)



# Password is encrypted then added to the encrypted passwords SQLite table
def add_pw(user, mode) -> None: 
    print( logo + line )
    new_category = str(input("Category: "))
    new_acct = str(input("Account: "))
    new_username = str(input("Username: "))
    new_pw = str(input("Password: "))

    # Check all fields are populated before proceeding
    if fieldNotEmpty(new_category, new_acct, new_username, new_pw):
        print(mode + doing)
        save_pw = encrypt_pw(new_pw)
        sqlite.insert_data(user, new_category, new_acct, new_username, save_pw, session_pw_key.decode(), today)

        # Return to Start Menu or repeat
        try_again( user, mode, new_acct, (done[0]))
    else:
        print("All fields are required")
        add_pw(user)


# Update password
def update_pw(user, list_pw, index, mode) -> None:
    # Before updating the password we need to save the returned account and username for the update statement
    # Ran into errors when using list_pw[index][1 or 0] directly in the SQLite update statement
    acct = str(list_pw[index][2])
    usr = str(list_pw[index][3])
    old_pw = str(list_pw[index][-3])

    replace_pw = str(input("New Password: "))
    if fieldNotEmpty(replace_pw):
        print(mode + doing)
        save_pw = encrypt_pw(replace_pw)
        sqlite.update_data(save_pw, acct, usr, old_pw, session_pw_key.decode(), today)

        # Return to Start Menu or repeat
        try_again(user, mode, (list_pw[index][2]), (done[0]))
    else:
        print("New password was not entered")
        # Return to Start Menu or repeat
        try_again(user, mode, (list_pw[index][2]), (done[0]))


# Delete password
def delete_pw(user, list_pw, index, mode) -> None:
    # Before deleting the password we need to save the returned account and username for the delete statement
    acct = str(list_pw[index][2])
    usr = str(list_pw[index][3])
    old_pw = str(list_pw[index][-3])

    # Check if the user wants to delete the chosen pw
    statement = (f"{Fore.YELLOW}{line}{Fore.WHITE}Are you sure you want to delete the password for {Fore.YELLOW}{list_pw[index][2]}{Fore.WHITE} ?")
    if yes_no( statement, user, mode, confirmDelete=True ) == True:
        # Success statement needs to slice first letter off mode
        print(mode[:-1] + doing)
        # Delete data from SQLite table
        sqlite.delete_data(user, acct, usr, old_pw)
        # Return to Start Menu or repeat
        # Success statement needs to slice first letter off mode
        # Other funcs incl edit, add, drecypted so deleteed is wrong
        try_again(user, mode, (list_pw[index][2]), (done[0][1:]))
    else:
        do_action(user, mode)


# Display password
def display_pw(user, list_pw, index, mode) -> None:
    # Before decrypting the password we need to save the returned Encryption Key for that record
    pw_key = list_pw[index][-2]
    pw = list_pw[index][-3]
    decrypted_pw = decrypt_pw(pw_key, pw)
    print(mode + doing)
    # Decrypt then return to Start Menu or repeat
    try_again((list_pw[index][0]), mode, (list_pw[index][2]), (done[0]), decrypted_pw)


def display_table(list_pw, selected_index):
    system('cls')
    print( logo + line + "\n" + navigation + features )

    # Create intermediary list to display data to Terminal with Tabulate
    list_table = []
    place = 1
    for i in list_pw:
        list_table.append([place, i[1], i[2], i[3], i[-3], i[-1]])
        place += 1

    # Print the headers
    print(tabulate([], headers=["Index", "Category", "Account", "Username", "Password", "Last Modified"], tablefmt="plain"))

    # Display the table rows starting from the first row
    for i, row in enumerate(list_table):
        if i == selected_index:
            # Highlight the current row
            print(Back.WHITE + Fore.BLACK + tabulate([row], headers=[], tablefmt="plain") + Style.RESET_ALL)
        else:
            print(tabulate([row], headers=[], tablefmt="plain"))

    # Dump intermediary list after use
    list_table = []


def search_pw(user, mode):
    # Empty FeatureVariable incase it already has a value of somekind
    featureVariable = []

    data = [
        "Category",
        "Account",
        "Username"
        ]

    selected_index = 0

    def display_options():
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
        display_options()
        key = readchar.readkey()

        if key == readchar.key.UP:
            selected_index = (selected_index - 1) % len(data)
        elif key == readchar.key.DOWN:
            selected_index = (selected_index + 1) % len(data)
        elif key == readchar.key.ENTER:
            # Add the selected Category to the FeatureVariable List
            searchCategory = data[selected_index]
            featureVariable.append(searchCategory.lower())
            break
        elif key == readchar.key.ESC:
            do_action(user, mode)
            break

    # Add the user input text to the FeatureVariable List
    searchText = input(f"\nSearch {searchCategory} for: ")
    featureVariable.append(searchText.lower())

    do_action(user, mode, featureVariable, feature="Search")


def sort_pw(user, mode):
    # Empty FeatureVariable incase it already has a value of somekind
    featureVariable = []

    data = [
        "Category",
        "Account",
        "Username"
        ]

    selected_index = 0

    def display_options():
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
        display_options()
        key = readchar.readkey()

        if key == readchar.key.UP:
            selected_index = (selected_index - 1) % len(data)
        elif key == readchar.key.DOWN:
            selected_index = (selected_index + 1) % len(data)
        elif key == readchar.key.ENTER:
            # Add the selected Category to the FeatureVariable List
            sortCategory = data[selected_index]
            featureVariable.append(sortCategory.lower())
            break
        elif key == readchar.key.ESC:
            do_action(user, mode)
            break

    data = [
        "Ascending",
        "Descending"
        ]

    selected_index = 0

    def display_options():
        system('cls')
        print(f"{navigation}\n Sort By {sortCategory}:\n")

        # Display the options with highlighted row
        for i, row in enumerate(data):
            if i == selected_index:
                # Highlight the current row
                print(Back.WHITE + Fore.BLACK + row + Style.RESET_ALL)
            else:
                print(row)

    while True:
        display_options()
        key = readchar.readkey()

        if key == readchar.key.UP:
            selected_index = (selected_index - 1) % len(data)
        elif key == readchar.key.DOWN:
            selected_index = (selected_index + 1) % len(data)
        elif key == readchar.key.ENTER:
            # Add the selected Category to the FeatureVariable List
            sortBy = data[selected_index]
            # Convert sortBy fromm Ascending to asc or Descending to desc
            featureVariable.append(sortBy.upper()[:-6])
            break
        elif key == readchar.key.ESC:
            do_action(user, mode)
            break

    do_action(user, mode, featureVariable, feature="Sort")


# Create new master password
def new_Master() -> None:
    new_master_user = str(input("Create new master user: "))
    new_master_pw = str(input("Create new master password: "))

    # Check all fields are populated before proceeding
    if fieldNotEmpty(new_master_user, new_master_pw):
        print("Adding new master password...")
        save_pw = encrypt_pw(new_master_pw)
        sqlite.insert_master(new_master_user, save_pw, session_pw_key.decode(), today)
        #  Write to log file
        logging(message = f"New master user and password created for {new_master_user}")
        # Return to Log In screen
        TerminalLogIn()
    else:
        print("1 or more required fields is missing!")
        new_Master()


# Create new master password
def update_Master(user) -> None:
    print( logo + line )
    new_master_pw = str(input("Enter new master password: "))

    # Check all fields are populated before proceeding
    if fieldNotEmpty(new_master_pw):
        print("Editing master password...")
        save_pw = encrypt_pw(new_master_pw)
        sqlite.update_master_pw(user, save_pw, session_pw_key.decode(), today)
        #  Write to log file
        logging(message = f"Master password updated for {user}")
        # Return to Log In screen
        TerminalLogIn()
    else:
        print("No password was entered!")
        update_Master(user)


# Handles user inputted values raising errors or out of range of list
def go_home(user, wrong) -> None:
    # Clear Terminal and print Logo
    system("cls")
    print( logo + line )
    statement = ( f"{Fore.RED}{line}{Fore.WHITE}\nYou entered {Fore.RED}{wrong}{Fore.WHITE}, which is not a valid selection.\n{go_back}")
    yes_no(statement, user, mode=0)


# The list_pw list is empty - user chooses to return to Start or Exit
def empty(user, mode) -> None:
    statement =  ( empty_list[0] + mode.lower() + empty_list[1] + go_back )
    yes_no(statement, user, mode=0)


# User chooses to perform the function again or return to Start
# Ran into issues using the yes_no function because this calls the extra argument of func
def try_again( user, mode, acct, fixed_done, pw=None) -> None:
    #  Write to log file
    logging(message = f"{mode}{fixed_done} {acct}")
    if mode == "Decrypt":
        statement = ( f"\n{pw}\n{Fore.GREEN}{line}{Fore.WHITE}" + mode + fixed_done + f"{Fore.GREEN}{acct}{Fore.WHITE}" + done[1] )
    else:
        statement = ( f"{Fore.GREEN}{line}{Fore.WHITE}" + mode + fixed_done + f"{Fore.GREEN}{acct}{Fore.WHITE}" + done[1] )
    yes_no(statement, user, mode)


# Handles Yes No choices
def yes_no(statement, user, mode, confirmDelete=None) -> None:

    selected_index = 0
    
    if confirmDelete:
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
    else:
        options = [
            f"{mode} Another Password",
            "Main Menu",
            "Quit"
            ]

    def choice_menu():
        system('cls')
        print(f"{logo}\n{statement}\n{navigation}")
        for i, option in enumerate(options):
            if i == selected_index:
                # Highlight current option
                print(f"{Back.WHITE}{Fore.BLACK}{option}{Style.RESET_ALL}")
            else:
                print(option)

    while True:
        choice_menu()
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
            elif options[selected_index] == f"{mode} Another Password":
                # To try_again we need to pass func variable as an argument when calling func variable
                # Because each function expects a func argument so it can call try_again() if needed
                do_action(user, mode)
            elif options[selected_index] == "Main Menu":
                Start(user)
            elif options[selected_index] ==  "Quit":
                print("Exiting...")
                exit()


# Encrypt
def encrypt_pw(pw) -> str:
    # Password is encoded then saved to a new variable per documentation
    encrypted_pw = fernet.encrypt(pw.encode())
    # The variable needs var.decode() when adding to the encrypted passwords table
    # This converts the values datatype from BITS to STRING
    # Otherwise it saves to the list as b'var' instead of 'var'
    # Decode is different to Decrypt, remember to read the docs more
    # The encoded pw is BITS datatype once encrypted and needs it's own variable
    return encrypted_pw.decode()


# Decrypt
def decrypt_pw(key, pw) -> str:
    # Decrypted password needs to be saved to its own variable
    # We use Fernet(pw_key) here instead of fernet variable to
    # Decrypt with the relevant records Encryption Key
    decrypted_pw = Fernet(key).decrypt(pw)
    # Remember to DECODE the new variable to convert from BITS datatype to STRING
    # This removes the leading b value changing b'variable' to 'variable'
    return decrypted_pw.decode()


# Write to Log file
def logging(message):
    f = open(".\\Logs.txt", "a")
    f.write(f"[{todaysTime}] {message}\n")
    f.close()


# Start CLI Guard in Terminal
if __name__ == "__main__":
    TerminalLogIn()