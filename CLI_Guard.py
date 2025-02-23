# Simple Password Manager SQL
import  SQL_DB.CLI_Guard_SQL as sqlite

# Tabulate is used to output list_pw and list_master data to Terminal in grid format
from tabulate import tabulate

# Colour text and others
from colorama import Fore, Back

# OS is imported to send 'cls' to the Terminal between functions
from os import system

# DateTime used when editing passwords or adding new passwords
from datetime import date, datetime, timedelta

today = date.today()
todaysTime = datetime.now().strftime('%Y-%m-%d %H:%M')
tomorrow = date.today() + timedelta(1)

# Import Python Cryptography library and Fernet module according to documentation
import cryptography
from cryptography.fernet import Fernet

# Import Glob to search for Files
import glob

# Import PyGetWindow to get current CLI size
import pygetwindow as gw



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

y_n = "Type Y for Yes or N for No\n(y/n)\n"
another = f" another password?\n{y_n}"
select = ["Select a password to ", " by typing the index of the account: "]
doing = "ing password..."
done = ["ed password for ", "...\n"]
empty_list = ["There are no passwords to ", "...\n"]
go_back = "Return to Start Menu?\n"
mode = ""
line = f"\n###################################################################################\n"
incorrect = "Incorrect password entered 3 times"



# Attempt Log In if user exists
def TerminalLogIn() -> None:
    # Clear Terminal then SPLASH
    system("cls")

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
        user_logging(message = f"[{todaysTime}] {incorrect}\n[{todaysTime}] Account locked until {tomorrow}")
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
        ("Exit", "exit")
    ]

    # Print CLI Splash for program Start
    print( splash + line )
    # List available functions by human-readable index
    for func in funcs:
        print(((funcs.index(func) + 1)), func[0])

    # TRY/EXCEPT handles if input is not INT
    try:
        # User chooses function, later converted to INT for comparison
        # Choice variable is not set as INT initially to avoid TRY/EXCEPT issues encounted
        choice = input(f"Select an option by typing 1-{len(funcs)}:\n")
        # Check choice is within range of funcs list or else raise error
        if int(choice) <= len(funcs):
            # Exit if users chooses exit, exit() does not take args that do_action takes
            if int(choice) == len(funcs):
                print("Exiting...")
                exit()
            else:
                # Loop through funcs list skipping where func != choice
                for func in funcs:
                    if int(choice) != ((funcs.index(func) + 1)):
                        continue
                # Execute chosen function
                    else:
                        # We need to pass func variable as an argument when calling func variable
                        # Because each function expects a func argument so it can call try_again() if needed
                        do_action(user, mode=func[-1])
        # This handles when input is outside of list range
        else:
            go_home(user, choice)
    # Try/Except handles Valueerrors raised when user inputs anything other than an INT
    except ValueError:
        go_home(user, choice)


# Get func arg then perform action
def do_action(user, mode) -> None:
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
                print( logo + line )
                # Query the passwords table and insert all into list_pw ordered by account name
                list_pw = sqlite.query_data(table = "passwords")

                # Check if list_pw is empty
                if listNotEmpty(list_pw):
                    # Use Tabulate to print selected columns to ternimal
                    display_passwords = display_all_pw(list_pw)
                    print(display_passwords)

                    # TRY/EXCEPT handles if input is not INT
                    try:
                        # User chooses record to perform action against
                        index = int(int(input( line + select[0] + mode.lower() + select[1] )) - 1 )

                        # Check if user input for index veriable is within the range of list_pw
                        if int(index) <= len(list_pw):

                            # Execute func (func == i[0]) with required args
                            func[0]((list_pw[index][0]), list_pw, index, mode)

                        # This handles when the index variable is outside of the range of list_pw
                        else:
                            go_home((list_pw[index][0]), (int(index) + 1))
                    # Try/Except handles Valueerrors raised when user inputs anything other than an INT
                    # Reference index variable instead of (index + 1) since this handles when index is STRING
                    except ValueError:
                        go_home(user, index)
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
        try_again(user, mode, new_acct, (done[0]))
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
    sure = str(input(f"{Fore.YELLOW}{line}{Fore.WHITE}Are you sure you want to delete the password for {Fore.YELLOW}{list_pw[index][2]}{Fore.WHITE} ?\n{y_n}"))
    if sure.lower() == "y":
        # Success statement needs to slice first letter off mode
        print(mode[:-1] + doing)
        # Delete data from SQLite table
        sqlite.delete_data(user, acct, usr, old_pw)
    elif sure.lower() == "n":
        Start(user)
    else:
        go_home(user, sure)
    # Return to Start Menu or repeat
    # Success statement needs to slice first letter off mode
    # Other funcs incl edit, add, drecypted so deleteed is wrong
    try_again(user, mode, (list_pw[index][2]), (done[0][1:]))


# Display password
def display_pw(user, list_pw, index, mode) -> None:
    # Before decrypting the password we need to save the returned Encryption Key for that record
    pw_key = list_pw[index][-2]
    pw = list_pw[index][-3]

    print(mode + doing)
    decrypted_pw = decrypt_pw(pw_key, pw)
    print(f"\n{decrypted_pw}\n")

    # Return to Start Menu or repeat
    try_again((list_pw[index][0]), mode, (list_pw[index][2]), (done[0]))


def display_all_pw(list_pw) -> str:
    # Create intermediary list to display data to Terminal with Tabulate
    list_table = []
    place = 1
    # Loop through the contents of list_pw to place in list_table since Tabulate won't allow to
    # Omit certain fields, this allows us to use the returned data as vairables without displaying in output
    for i in list_pw:
        list_table.append([place, i[1], i[2], i[3], i[-3], i[-1]])
        place += 1

    data = (tabulate(list_table, headers=["Index", "Category", "Account", "Username", "Password", "Last Modified"], numalign="center"))

    # Dump intermediary list after use
    list_table = []

    return data


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
        user_logging(message = f"[{todaysTime}] New master user and password created for {new_master_user}\n")
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
        user_logging(message = f"[{todaysTime}] Master password updated for {user}\n")
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
    print( f"{Fore.RED}{line}{Fore.WHITE}\nYou entered {Fore.RED}{wrong}{Fore.WHITE}, which is not a valid selection.")
    home = str(input( go_back + y_n ))
    yes_no(user, home, mode=0)


# The list_pw list is empty - user chooses to return to Start or Exit
def empty(user, mode) -> None:
    home = str(input( empty_list[0] + mode.lower() + empty_list[1] + go_back + y_n ))
    yes_no(user, home, mode=0)


# User chooses to perform the function again or return to Start
# Ran into issues using the yes_no function because this calls the extra argument of func
def try_again(user, mode, acct, fixed_done) -> None:
    #  Write to log file
    user_logging(message = f"[{todaysTime}] {mode}{fixed_done} {acct}\n")
    again = str(input( f"{Fore.GREEN}{line}{Fore.WHITE}" + mode + fixed_done + f"{Fore.GREEN}{acct}{Fore.WHITE}" + done[1] + mode + another ))
    yes_no(user, again, mode)


# Handles Yes No choices
def yes_no(user, choice, mode) -> None:
    if mode == 0:
        if choice.lower() == "y":
            Start(user)
        elif choice.lower() == "n":
            print("Exiting...")
            exit()
        else:
            go_home(user, choice) 
    else:
        if choice.lower() == "y":
            # To try_again we need to pass func variable as an argument when calling func variable
            # Because each function expects a func argument so it can call try_again() if needed
            do_action(user, mode)
        elif choice.lower() == "n":
            Start(user)
        else:
            go_home(user, choice)


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


#  Write to all Log files so that Debug Logging contains all Logs and User Logging is less verbose
def user_logging(message):
# Find Log files
    log_files = glob.glob(".\\Logs\Logs*.txt")
    # Iterate over each Log file and append the message
    for file in log_files:
        with open(file, "a") as f:
            f.write(message)
            f.close()


# Write to Debugging Log file
def debug_logging(error_message):
    f = open(".\\Logs\Logs_Debugging.txt", "a")
    f.write(error_message)
    f.close()


# Start CLI Guard in Terminal
if __name__ == "__main__":
    TerminalLogIn()