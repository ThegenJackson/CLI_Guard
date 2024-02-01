# Import SQLite library
import sqlite3

# Import Python Cryptography library and Fernet module according to documentation
import cryptography
from cryptography.fernet import Fernet

# Tabulate is used to output list_pw data to terminal in grid format
from tabulate import tabulate

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

# Create empty list of encrypted passwords and persistent key
list_pw = []
list_keys = []

# Formatting terminal output
# Not all message-pieces should be kept in a list
# Overuse of lists for message-pieces makes creating messages confusing
splash = f"""                                           
   SSSSSSSSSSSSSSS      PPPPPPPPPPPPPPPPP       MMMMMMMM               MMMMMMMM
 SS:::::::::::::::S     P::::::::::::::::P      M:::::::M             M:::::::M
S:::::SSSSSS::::::S     P::::::PPPPPP:::::P     M::::::::M           M::::::::M
S:::::S     SSSSSSS     PP:::::P     P:::::P    M:::::::::M         M:::::::::M
S:::::S                   P::::P     P:::::P    M::::::::::M       M::::::::::M
S:::::S                   P::::P     P:::::P    M:::::::::::M     M:::::::::::M
 S::::SSSS                P::::PPPPPP:::::P     M:::::::M::::M   M::::M:::::::M
  SS::::::SSSSS           P:::::::::::::PP      M::::::M M::::M M::::M M::::::M
    SSS::::::::SS         P::::PPPPPPPPP        M::::::M  M::::M::::M  M::::::M
       SSSSSS::::S        P::::P                M::::::M   M:::::::M   M::::::M
            S:::::S       P::::P                M::::::M    M:::::M    M::::::M
            S:::::S       P::::P                M::::::M     MMMMM     M::::::M
SSSSSSS     S:::::S     PP::::::PP              M::::::M               M::::::M
S::::::SSSSSS:::::S     P::::::::P              M::::::M               M::::::M
S:::::::::::::::SS      P::::::::P              M::::::M               M::::::M
 SSSSSSSSSSSSSSS        PPPPPPPPPP              MMMMMMMM               MMMMMMMM

                            Simple Password Manager                                                           
"""
line = "##################################################################################\n"
yes_no = "Type Y for Yes or N for No\n(y/n)\n"
another = f" another password?\n{yes_no}"
select = ["Select a password to ", " by typing the index of the account: "]
doing = "ing password..."
done = ["ed password for ", "...\n"]
empty_list = ["There are no passwords to ", "...\nReturn to Start Menu?\n"]
create_key = "                         Create a new Persistent Key:\n"
mode = ""



# Display Splash and Start Menu to CLI - User chooses function
def start():
    # Define function index, human-readable text, function name
    funcs = [
        (1, "Create new password", add_pw),
        (2, "Edit a password", edit_pw),
        (3, "Delete a password", del_pw),
        (4, "Display a password", show_pw),
        (5, "Exit", exit)
    ]

    # Print CLI Splash for program Start
    print( line + splash + line )
    # List available functions by human-readable index
    for i in funcs:
        print(i[0], i[1])

    # User chooses function converted to INT for comparison
    choice = int(input("Select an option:\n"))

    # Loop through funcs list, skipping where function != chosen
    for i in funcs:
        if i[0] != choice:
            continue
        else:
            # Execute chosen function
            i[-1]()


# Check if persistent_key exists - needed to decrypt session_pw_key in later sessions
# The persistent_key is used to decrypt encrypted Fernet Keys in later sessions
# The persistent_key is constant to allow easy decryption of the Fernet Keys generated in each new session
def checks():
    # Query the keys table and return the persistent key
    # Save query results in empty list_keys
    sql_cursor.execute("""
                       SELECT * 
                       FROM keys;
                       """)
    list_keys = sql_cursor.fetchone()
    # Check a real value is returned
    if list_keys is None:
        add_key()
    else:
        start()


# Add persistent_key to database
def add_key():
    # Double check the SQL query returns a None type before
    # Executing INSERT statement as only 1 persistent_key should exist
    # If statement reversed from checks() function as triple-check measure
    # Query the keys table and return the persistent key
    sql_cursor.execute("""
                       SELECT * 
                       FROM keys;
                       """)
    list_keys = sql_cursor.fetchone()
    # Check a real value is returned
    # If statement reversed from checks() function as triple-check measure
    if list_keys is not None:
        start()
    else:
        # User inputs persistent_key STRING value
        persistent_key = str(input( splash + create_key ))
        # Insert persistent_key value into keys table
        sql_cursor.execute(f"""
                        INSERT INTO keys 
                        VALUES('{persistent_key}');
                        """)
        sql_connection.commit()
        # Perform required checks before program Start
        checks()


def edit_key():
    print("more dev work needed")


# User inputs account, username and password
# Password is encrypted then added to the encrypted passwords table
def add_pw():
    mode = "Add"   
    new_acct = str(input("Account: "))
    new_username = str(input("Username: "))
    new_pw = str(input("Password: "))
    
    if new_acct != "" and new_username != "" and new_pw != "":
        print(mode + doing)
        # User inputted value for new_pw is encoded then saved to a new variable per documentation
        encoded_pw = fernet.encrypt(new_pw.encode())
        # The variable needs var.decode() when adding to the encrypted passwords table
        # This converts the values datatype from BITS to STRING
        # Otherwise it saves to the list as b'var' instead of 'var'
        # Decode is different to Decrypt, remember to read the docs more
        # The encoded pw is BITS datatype once encrypted and needs it's own variable
        sql_cursor.execute(f"""
                        INSERT INTO passwords 
                        VALUES(
                           '{new_acct}',
                           '{new_username}',
                           '{encoded_pw.decode()}',
                           '{session_pw_key.decode()}',
                           '{today}');
                        """)
        sql_connection.commit()

        # Return to Start Menu or repeat
        again = str(input( line + mode + done[0] + new_acct + done[1] + mode + another ))
        if again.lower() == "y":
            add_pw()
        else:
            start()
    else:
        print("All fields are required")
        add_pw()


# Edit a password from the encrypted passwords table based on it's index
def edit_pw():
    mode = "Edit"
    print(line)

    # Query the passwords table and insert all into list_pw ordered by account name
    sql_cursor.execute("""
                       SELECT * 
                       FROM passwords 
                       ORDER BY account ASC;
                       """)
    list_pw = sql_cursor.fetchall()

    # Check if list_pw is empty to avoid app crash when input expects user to give index of record that exists
    if list_pw != []:
        # Create intermediary list to display data to terminal with Tabulate
        list_table = []
        place = 1
        # Loop through the contents of list_pw to place in list_table since Tabulate won't allow to
        # Omit certain fields, this allows us to use the returned data as vairables without displaying in output
        for i in list_pw:
            list_table.append([place, i[0], i[-3], i[-1]])
            place += 1
        print(tabulate(list_table, headers=["Index", "Account", "Password", "Last Modified"], numalign="center"))

        # Dump intermediary list after use
        list_table = []

        # User chooses a record that corresponds with record row when ORDER BY account ASC
        index = int(int(input( line + select[0] + mode.lower() + select[1] )) - 1)

        # Before updating the password we need to save the returned account and username for the update statement
        # Ran into errors when using list_pw[index][1 or 0] directly in the SQLite update statement
        acct = str(list_pw[index][0])
        usr = str(list_pw[index][1])
        
        replace_pw = str(input("New Password: "))
        print(mode + doing)
        # User input value for replace_pw is encoded then saved to a new variable
        replace_encoded_pw = fernet.encrypt(replace_pw.encode())
        # Remember the new variable needs to be DECODED before adding to the encrypted passwords table
        # This converts the values datatype from BITS to STRING
        sql_cursor.execute(f"""
                        UPDATE passwords 
                        SET password = '{replace_encoded_pw.decode()}', 
                        pw_key = '{session_pw_key.decode()}',
                        last_modified = '{today}' 
                        WHERE account = '{acct}' 
                        AND username = '{usr}';
                        """)
        sql_connection.commit()

        # Return to Start Menu or repeat
        again = str(input( line + mode + done[0] + list_pw[index][0] + done[1] + mode + another ))
        if again.lower() == "y":
            edit_pw()
        else:
            start()
    else:
        home = str(input( empty_list[0] + mode.lower() + empty_list[1] + yes_no ))
        if home.lower() == "y":
            start()
        else:
            exit()


# Remove a password from the encrypted passwords table based on it's index
def del_pw():
    mode = "Delete"
    print(line)

    # Query the passwords table and insert all into list_pw ordered by account name
    sql_cursor.execute("""
                       SELECT * 
                       FROM passwords 
                       ORDER BY account ASC;
                       """)
    list_pw = sql_cursor.fetchall()

    # Check if list_pw is empty to avoid app crash when input expects user to give index of record that exists
    if list_pw != []:
        # Create intermediary list to display data to terminal with Tabulate
        list_table = []
        place = 1
        # Loop through the contents of list_pw to place in list_table since Tabulate won't allow to
        # Omit certain fields, this allows us to use the returned data as vairables without displaying in output
        for i in list_pw:
            list_table.append([place, i[0], i[-3], i[-1]])
            place += 1
        print(tabulate(list_table, headers=["Index", "Account", "Password", "Last Modified"], numalign="center"))

        # Dump intermediary list after use
        list_table = []

        index = int(int(input( line + select[0] + mode.lower() + select[1] )) - 1)

        # Before deleting the password we need to save the returned account and username for the delete statement
        acct = str(list_pw[index][0])
        usr = str(list_pw[index][1])

        # Check if the user wants to delete the chosen pw
        sure = str(input(f"{line}Are you sure you want to delete the password for {list_pw[index][0]} ?\n{yes_no}"))
        if sure.lower() == "y":
            # Success statement needs to slice first letter off mode
            print(mode[:-1] + doing)
            sql_cursor.execute(f"""
                            DELETE FROM passwords 
                            WHERE account = '{acct}' 
                            AND username = '{usr}';
                            """)
            sql_connection.commit()
        elif sure.lower() == "n":
            start()

        # Return to Start Menu or repeat
        # Success statement needs to slice first letter off mode
        # Other funcs incl edit, add, drecypted so deleteed is wrong
        again = str(input( line + mode[:-1] + done[0] + list_pw[index][0] + done[1] + mode + another ))
        if again.lower() == "y":
            del_pw()
        else:
            start()
    else:
        home = str(input( empty_list[0] + mode.lower() + empty_list[1] + yes_no ))
        if home.lower() == "y":
            start()
        else:
            exit()


# Choose a password to display based on it's index in the encrypted passwords table
def show_pw():
    mode = "Decrypt"
    print(line)

    # Query the passwords table and insert all into list_pw ordered by account name
    sql_cursor.execute("""
                       SELECT * 
                       FROM passwords 
                       ORDER BY account ASC;
                       """)
    list_pw = sql_cursor.fetchall()

    # Check if list_pw is empty to avoid app crash when input expects user to give index of record that exists
    if list_pw != []:
        # Create intermediary list to display data to terminal with Tabulate
        list_table = []
        place = 1
        # Loop through the contents of list_pw to place in list_table since Tabulate won't allow to
        # Omit certain fields, this allows us to use the returned data as vairables without displaying in output
        for i in list_pw:
            list_table.append([place, i[0], i[-3], i[-1]])
            place += 1
        print(tabulate(list_table, headers=["Index", "Account", "Password", "Last Modified"], numalign="center"))

        # Dump intermediary list after use
        list_table = []

        index = int(int(input( line + select[0] + mode.lower() + select[1] )) - 1)

        # Before decrypting the password we need to save the returned Encryption Key for that record
        pw_key = list_pw[index][-2]

        print(mode + doing)
        # Decrypted password needs to be saved to its own variable
        # We use Fernet(pw_key) here instead of fernet variable to
        # Decrypt with the relevant records Encryption Key
        decoded_pw = Fernet(pw_key).decrypt(list_pw[index][-3])
        # Remember to decode the new variable to convert from BITS datatype to STRING
        # This removes the leading b value changing b'variable' to 'variable'
        print(f"\n{decoded_pw.decode()}\n")

        # Return to Start Menu or repeat
        again = str(input( line + mode + done[0] + list_pw[index][0] + done[1] + mode + another ))
        if again.lower() == "y":
            show_pw()
        else:
            start()
    else:
        home = str(input( empty_list[0] + mode.lower() + empty_list[1] + yes_no ))
        if home.lower() == "y":
            start()
        else:
            exit()


# Start the CLI app
checks()
