# ###########################################################################
#                          Author: Thegen Jackson
# ###########################################################################
#   Document design decisions on relevant Confluence page
#   - Update Confluence to link to all relevant Docs needed
#   - Decided to use Agile development framework prioritizing function first,
#      documentation to follow
#   - Decided to use SQLite over MySQL due to SQLite being more lightweight
#      and restricted to only 1 user
#   - Decided to split the app into CLI app as well as GUI app
#   - Terminal app to be saved as SPM.py, execute at CLI with "python SPM.py"
#   - GUI app to use Tkinter and to be packed into .exe
#   - GUI to be saved as SimplePasswordManager.exe
#   - Both CLI and GUI apps to access same DB
# ###########################################################################

# Import Python Cryptography library and Fernet module according to documentation
import cryptography
from cryptography.fernet import Fernet

# DateTime used when editing passwords or adding new passwords
from datetime import date


today = date.today()

#Generate the Fernet encryption key
# Required for encryption and decryption with Fernet as per documentation
key = Fernet.generate_key()
fernet = Fernet(key)

# Create empty list of encrypted passwords
list_pw = []

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
done = ["ed password for ", "...\n"]
mode = ""


# Display Splash and Start Menu to CLI - User chooses function
def start():
    print(f"{line + splash + line}Select an option:\n1. Create new password\n2. Edit a password\n3. Delete a password\n4. Display a password\n5. Exit\n{line}")
    choice = input()
    if choice == '1':
        add_pw()
    elif choice == '2':
        edit_pw()
    elif choice == '3':
        del_pw()
    elif choice == '4':
        show_pw()
    elif choice == '5':
        exit()
    else:
        print(f"{line}Choose by typing a number between 1 and 5")
        start()


# User inputs account, username and password
# Password is encrypted then added to the encrypted passwords list
def add_pw():
    mode = "Add"   
    new_acct = str(input("Account: "))
    new_username = str(input("Username: "))
    new_pw = str(input("Password: "))
    # User inputted value for new_pw is encoded then saved to a new variable per documentation
    encoded_pw = fernet.encrypt(new_pw.encode())
    # The variable needs var.decode() when adding to the encrypted passwords list
    # This converts the values datatype from BITS to STRING
    # Otherwise it saves to the list as b'var' instead of 'var'
    # Decode is different to Decrypt, remember to read the docs more
    # The encoded pw is BITS datatype once encrypted and needs it's own variable
    list_pw.append([new_acct, new_username, encoded_pw.decode(), today])

    # Return to Start Menu or repeat
    again = str(input( line + mode + done[0] + new_acct + done[1] + mode + another ))
    if again.lower() == "y":
        add_pw()
    else:
        start()


# Edit a password from the encrypted passwords list based on it's index
def edit_pw():
    mode = "Edit"
    print(line)
    # List contents of encrypted passwords list in human-readable format
    place = 1
    for i in list_pw:
        print(place, " | ", i[0], " | ", i[-2], " | ", i[-1])
        place += 1

    index = int(int(input( line + select[0] + mode.lower() + select[1] )) - 1)

    replace_pw = str(input("New Password: "))
    # User input value for replace_pw is encoded then saved to a new variable
    replace_encoded_pw = fernet.encrypt(replace_pw.encode())
    # Issues arise when assigning the value directly to the sub-list index
    # To avoid this we first remove the last value in the relevant sub-list
    # Then append the decoded variable to the relevant sub-list
    # Remember the value needs to be decoded before adding to the encrypted passwords list
    # This converts the values datatype from BITS to STRING
    list_pw[index].remove(list_pw[index][-2:])
    list_pw[index].append([replace_encoded_pw.decode(), today])

    # Return to Start Menu or repeat
    again = str(input( line + mode + done[0] + list_pw[index][0] + done[1] + mode + another ))
    if again.lower() == "y":
        edit_pw()
    else:
        start()


# Remove a password from the encrypted passwords list based on it's index
def del_pw():
    mode = "Delete"
    print(line)
    # List contents of encrypted passwords list in human-readable format
    place = 1
    for i in list_pw:
        print(place, " | ", i[0], " | ", i[-2], " | ", i[-1])
        place += 1

    index = int(int(input( line + select[0] + mode.lower() + select[1] )) - 1)

    # Check if the user wants to delete the chosen pw
    sure = str(input(f"{line}Are you sure you want to delete the password for {list_pw[index][0]} ?\n{yes_no}"))
    if sure.lower() == "y":
        list_pw.remove(list_pw[index])
    elif sure.lower() == "n":
        start()

    # Return to Start Menu or repeat
    # Success statement needs to slice first letter off from done[0]
    # Other funcs incl edit, add, drecypted so deleteed is wrong
    again = str(input( line + mode + (done[0])[1:] + list_pw[index][0] + done[1] + mode + another ))
    if again.lower() == "y":
        del_pw()
    else:
        start()


# Choose a password to display based on it's index in the encrypted passwords list
def show_pw():
    mode = "Decrypt"
    print(line)
    # List contents of encrypted passwords list in human-readable format
    place = 1
    for i in list_pw:
        print(place, " | ", i[0], " | ", i[-2], " | ", i[-1])
        place += 1

    index = int(int(input( line + select[0] + mode.lower() + select[1] )) - 1)

    # Similar to encrypting, the decrypted password needs to be stored in a new variable
    decoded_pw = fernet.decrypt(list_pw[index][-2])
    # Remember to decode the new variable to convert from BITS datatype to STRING
    # This removes the leading b value changing b'variable' to 'variable'
    print(f"\n{decoded_pw.decode()}\n")

    # Return to Start Menu or repeat
    again = str(input( line + mode + done[0] + list_pw[index][0] + done[1] + mode + another ))
    if again.lower() == "y":
        show_pw()
    else:
        start()

# Start the CLI app
start()
