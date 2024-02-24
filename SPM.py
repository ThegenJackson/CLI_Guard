# Simple Password Manager

# Import SPM Python packages
from SPM_CLI import *
from SPM_GUI import *
from SPM_API import *
from SPG import *

# Import SQLite library
import sqlite3

# Import Python Cryptography library and Fernet module according to documentation
import cryptography
from cryptography.fernet import Fernet

# Tabulate is used to output list_pw data to terminal in grid format
from tabulate import tabulate

# Colour the Splash and others
from colorama import Fore, Back

# OS is imported to send 'cls' to the terminal between functions
from os import system

# DateTime used when editing passwords or adding new passwords
from datetime import date


today = date.today()


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

# Connet to database file included in Simple Program Manager
sql_connection = sqlite3.connect('SPMdb.db')
# Create a cursor - read more docs on this
sql_cursor = sql_connection.cursor()

# Create empty list of encrypted passwords
list_pw = []

# Formatting terminal output
# Not all message-pieces should be kept in a list
# Overuse of lists for message-pieces makes creating messages confusing
splash = f"""                                           
   SSSSSSSSSSSSSSS      PPPPPPPPPPPPPPPPP       MMMMMMMM               MMMMMMMM
 SSSSSSSSSSSSSSSSSS     PPPPPPPPPPPPPPPPPP      MMMMMMMMM             MMMMMMMMM
SSSSSSSSSSSSSSSSSSS     PPPPPPPPPPPPPPPPPPP     MMMMMMMMMM           MMMMMMMMMM
SSSSSSS     S{Fore.GREEN}Simple{Fore.WHITE}     PPPPPPPP     PPPPPPP    MMMMMMMMMMM         MMMMMMMMMMM
SSSSSSS                   PPPPPP     PPPPPPP    MMMMMMMMMMMM       MMMMMMMMMMMM
SSSSSSS                   PPPPPP     PPPPPPP    MMMMMMMMMMMMM     MMMMMMMMMMMMM
 SSSSSSSSS                PPPPPPPPPPPPPPPPP     MMMMMMMMMMMMMM   MMMMMMMMMMMMMM
  SSSSSSSSSSSSS           PPPPPPPPPPPPPPPP      MMMMMMMM MMMMMM MMMMMM MMMMMMMM
    SSSSSSSSSSSSS         PPPPPP{Fore.GREEN}Password{Fore.WHITE}        MMMMMMMM  MMMMMMMMMMM  MMMMMMMM
       SSSSSSSSSSS        PPPPPP                MMMMMMMM   MMMMMMMMM   MMMMMMMM
            SSSSSSS       PPPPPP                MMMMMMMM    MMMMMMM    MMMMMMMM
            SSSSSSS       PPPPPP                MMMMMMMM     MMMMM     MMMMMMMM
SSSSSSS     SSSSSSS     PPPPPPPPPP              MMMMMMMM               MMMMMMMM
SSSSSSSSSSSSSSSSSSS     PPPPPPPPPP              MMMMMMMM               MMMMMMMM
SSSSSSSSSSSSSSSSSS      PPPPPPPPPP              MMMMMMMM               MMMMMMMM
 SSSSSSSSSSSSSSS        PPPPPPPPPP              M{Fore.GREEN}Manager{Fore.WHITE}               MMMMMMMM

                            {Fore.GREEN}Simple Password Manager{Fore.WHITE}                                                           
"""
y_n = "Type Y for Yes or N for No\n(y/n)\n"
another = f" another password?\n{y_n}"
select = ["Select a password to ", " by typing the index of the account: "]
doing = "ing password..."
done = ["ed password for ", "...\n"]
empty_list = ["There are no passwords to ", "...\n"]
go_back = "Return to Start Menu?\n"
mode = ""
line = f"##################################################################################\n"



# Display Splash and Start Menu to CLI - User chooses function
def start():
    # Clear Terminal
    system('cls')
    # Define function index, human-readable text, function name
    funcs = [
        (1, "Create new password", "Add"),
        (2, "Edit a password", "Edit"),
        (3, "Delete a password", "Delete"),
        (4, "Display a password", "Decrypt"),
        (5, "Exit")
    ]

    # Print CLI Splash for program Start
    print( line + splash + line )
    # List available functions by human-readable index
    for func in funcs:
        print(func[0], func[1])

    # TRY/EXCEPT handles if input is not INT
    try:
        # User chooses function, later converted to INT for comparison
        # Choice variable is not set as INT initially to avoid TRY/EXCEPT issues encounted
        choice = input(f"Select an option by typing 1-{len(funcs)}:\n")
        # Check choice is within range of funcs list or else raise error
        if int(choice) <= len(funcs):
            # Exit if users chooses exit, exit() does not take args that do_action takes
            if int(choice) == 5:
                print("Exiting...")
                exit()
            else:
                # Loop through funcs list skipping where func != choice
                for func in funcs:
                    if func[0] != int(choice):
                        continue
                # Execute chosen function
                    else:
                        # We need to pass func variable as an argument when calling func variable
                        # Because each function expects a func argument so it can call try_again() if needed
                        do_action(func[-1])
        # This handles when input is outside of list range
        else:
            go_home(choice)
    # Try/Except handles ValueError raised when user inputs anything other than an INT
    except ValueError:
        go_home(choice)


# Get func arg then perform action
def do_action(mode):
    # Clear Terminal
    system('cls')
    # Define function index and function name
    funcs = [
        (update_pw, "Edit"),
        (delete_pw, "Delete"),
        (display_pw, "Decrypt")
    ]

    if mode == "Add":
        add_pw(mode)
    else:
        for func in funcs:
            if func[-1] != mode:
                continue
            # Execute chosen function
            else:
                print(line)
                # Query the passwords table and insert all into list_pw ordered by account name
                list_pw = query_data()

                # Check if list_pw is empty
                if list_pw != []:
                    # Use Tabulate to print selected columns to ternimal
                    display_data = display(list_pw)
                    print(display_data)

                    # TRY/EXCEPT handles if input is not INT
                    try:
                        # User chooses record to perform action against
                        index = int(int(input( line + select[0] + mode.lower() + select[1] )) - 1 )
                        # Check if user input for index veriable is within the range of list_pw
                        if int(index) <= len(list_pw):

                            # Execute func (func == i[0]) with required args
                            func[0](list_pw, index, mode)

                        # This handles when the index variable is outside of the range of list_pw
                        else:
                            go_home((int(index) + 1))
                    # Try/Except handles ValueError raised when user inputs anything other than an INT
                    # Reference index variable instead of (index + 1) since this handles when index is STRING
                    except ValueError:
                        go_home(index)
                else:
                    empty(mode)
                        # We need to pass func variable as an argument when calling func variable
                        # Because each function expects a func argument so it can call try_again() if needed


# Password is encrypted then added to the encrypted passwords SQLite table
def add_pw(mode): 
    new_acct = str(input("Account: "))
    new_username = str(input("Username: "))
    new_pw = str(input("Password: "))

    # Check all fields are populated before proceeding
    if new_acct != "" and new_username != "" and new_pw != "":
        print(mode + doing)
        save_pw = encrypt_pw(new_pw)
        insert_data(new_acct, new_username, save_pw)

        # Return to Start Menu or repeat
        try_again(mode, new_acct, (done[0]))
    else:
        print("All fields are required")
        add_pw()


# Update password
def update_pw(list_pw, index, mode):
    # Before updating the password we need to save the returned account and username for the update statement
    # Ran into errors when using list_pw[index][1 or 0] directly in the SQLite update statement
    acct = str(list_pw[index][0])
    usr = str(list_pw[index][1])
    old_pw = str(list_pw[index][-3])

    replace_pw = str(input("New Password: "))
    if replace_pw != "":
        print(mode + doing)
        save_pw = encrypt_pw(replace_pw)
        update_data(save_pw, acct, usr, old_pw)

        # Return to Start Menu or repeat
        try_again(mode, (list_pw[index][0]), (done[0]))
    else:
        print("New password was not entered")
        # Return to Start Menu or repeat
        try_again(mode, (list_pw[index][0]), (done[0]))


# Delete password
def delete_pw(list_pw, index, mode):
    # Before deleting the password we need to save the returned account and username for the delete statement
    acct = str(list_pw[index][0])
    usr = str(list_pw[index][1])
    old_pw = str(list_pw[index][-3])

    # Check if the user wants to delete the chosen pw
    sure = str(input(f"{Fore.YELLOW}{line}{Fore.WHITE}Are you sure you want to delete the password for {Fore.YELLOW}{list_pw[index][0]}{Fore.WHITE} ?\n{y_n}"))
    if sure.lower() == "y":
        # Success statement needs to slice first letter off mode
        print(mode[:-1] + doing)
        # Delete data from SQLite table
        delete_data(acct, usr, old_pw)
    elif sure.lower() == "n":
        start()
    else:
        go_home(sure)
    # Return to Start Menu or repeat
    # Success statement needs to slice first letter off mode
    # Other funcs incl edit, add, drecypted so deleteed is wrong
    try_again(mode, (list_pw[index][0]), (done[0][1:]))


# Display password
def display_pw(list_pw, index, mode):
    # Before decrypting the password we need to save the returned Encryption Key for that record
    pw_key = list_pw[index][-2]
    pw = list_pw[index][-3]

    print(mode + doing)
    decrypted_pw = decrypt_pw(pw_key, pw)
    print(f"\n{decrypted_pw}\n")

    # Return to Start Menu or repeat
    try_again(mode, (list_pw[index][0]), (done[0]))

def display(list_pw):
    # Create intermediary list to display data to terminal with Tabulate
    list_table = []
    place = 1
    # Loop through the contents of list_pw to place in list_table since Tabulate won't allow to
    # Omit certain fields, this allows us to use the returned data as vairables without displaying in output
    for i in list_pw:
        list_table.append([place, i[0], i[-3], i[-1]])
        place += 1

    data = (tabulate(list_table, headers=["Index", "Account", "Password", "Last Modified"], numalign="center"))

    # Dump intermediary list after use
    list_table = []

    return data


# Encrypt
def encrypt_pw(pw):
    # Password is encoded then saved to a new variable per documentation
    encrypted_pw = fernet.encrypt(pw.encode())
    # The variable needs var.decode() when adding to the encrypted passwords table
    # This converts the values datatype from BITS to STRING
    # Otherwise it saves to the list as b'var' instead of 'var'
    # Decode is different to Decrypt, remember to read the docs more
    # The encoded pw is BITS datatype once encrypted and needs it's own variable
    return encrypted_pw.decode()


# Decrypt
def decrypt_pw(key, pw):
    # Decrypted password needs to be saved to its own variable
    # We use Fernet(pw_key) here instead of fernet variable to
    # Decrypt with the relevant records Encryption Key
    decrypted_pw = Fernet(key).decrypt(pw)
    # Remember to DECODE the new variable to convert from BITS datatype to STRING
    # This removes the leading b value changing b'variable' to 'variable'
    return decrypted_pw.decode()


# Handles user inputted values raising ValueErrors or out of range of list
def go_home(wrong):
    # Clear Terminal
    system('cls')
    print( f"{Fore.RED}{line}{Fore.WHITE}\nYou entered {Fore.RED}{wrong}{Fore.WHITE}, which is not a valid selection.")
    home = str(input( go_back + y_n ))
    yes_no(home, mode=0)


# The list_pw list is empty - user chooses to return to Start or Exit
def empty(mode):
    home = str(input( empty_list[0] + mode.lower() + empty_list[1] + go_back + y_n ))
    yes_no(home, mode=0)


# User chooses to perform the function again or return to Start
# Ran into issues using the yes_no function because this calls the extra argument of func
def try_again(mode, acct, fixed_done):
    again = str(input( f"{Fore.GREEN}{line}{Fore.WHITE}" + mode + fixed_done + f"{Fore.GREEN}{acct}{Fore.WHITE}" + done[1] + mode + another ))
    yes_no(again, mode)


# Handles Yes No choices
def yes_no(choice, mode):
    if mode == 0:
        if choice.lower() == "y":
            start()
        elif choice.lower() == "n":
            print("Exiting...")
            exit()
        else:
            go_home(choice) 
    else:
        if choice.lower() == "y":
            # To try_again we need to pass func variable as an argument when calling func variable
            # Because each function expects a func argument so it can call try_again() if needed
            do_action(mode)
        elif choice.lower() == "n":
            start()
        else:
            go_home(choice) 


# Query the passwords table and insert all into list_pw ordered by account name
def query_data():
    sql_cursor.execute("""
                        SELECT * 
                        FROM passwords 
                        ORDER BY account ASC;
                        """)
    list_pw = sql_cursor.fetchall()
    return list_pw


# INSERT new records into passwords SQLite table
def insert_data(acct, username, pw):
    sql_cursor.execute(f"""
                    INSERT INTO passwords 
                    VALUES(
                        '{acct}',
                        '{username}',
                        '{pw}',
                        '{session_pw_key.decode()}',
                        '{today}');
                    """)
    sql_connection.commit()


# UPDATE records in the passwords SQLite table
def update_data(pw, acct, usr, old_pw):
    sql_cursor.execute(f"""
                    UPDATE passwords 
                    SET password = '{pw}', 
                    pw_key = '{session_pw_key}',
                    last_modified = '{today}' 
                    WHERE account = '{acct}' 
                    AND username = '{usr}'
                    AND password = '{old_pw}';
                    """)
    sql_connection.commit()


# DELETE records from the passwords SQLite table
def delete_data(acct, usr, pw):
    sql_cursor.execute(f"""
                    DELETE FROM passwords 
                    WHERE account = '{acct}' 
                    AND username = '{usr}'
                    AND password = '{pw}';
                    """)
    sql_connection.commit()



# Start the CLI app
start()

# Start the program using the mainWindow
# mainWindow.mainloop()