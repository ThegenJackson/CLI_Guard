# Import tkinter - read more docs
import tkinter as tk

# Import Python Cryptography library and Fernet module according to documentation
import cryptography
from cryptography.fernet import Fernet


#Generate the Fernet encryption key
# Required for encryption and decryption with Fernet as per documentation
key = Fernet.generate_key()
fernet = Fernet(key)

# Create empty list of encrypted passwords
list_pw = []

# Formatting terminal output
line = "#######################################\n"
mode = ""
yes_no = " Type Y for Yes or N for No\n(y/n)\n"
another = f" another password?\n{yes_no}"
select = "Select a password to "
typing = " by typing the index of the account: "



# Program Start - User chooses function
def start():
    print(f"Simple Password Manager\nSelect an option:\n1. Create new password\n2. Edit a password\n3. Delete a password\n4. Display a password\n5. Exit\n{line}")
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
        print(f"{line}Choose by typing a number between 1 and 4")
        start()


# User inputs a password which is encrypted then added to the encrypted passwords list
def add_pw():
    mode = "Add"    
    new_acct = str(input("Account: "))
    new_username = str(input("Username: "))
    new_pw = str(input("Password: "))
    # User input value for new_pw is encoded then saved to a new variable
    encoded_pw = fernet.encrypt(new_pw.encode())
    # The variable needs var.decode() when adding to the encrypted passwords list
    # This converts the values datatype from BITS to STRING
    # Otherwise it saves to the list as b'var' instead of 'var'
    # Decode is different to Decrypt, remember to read the docs more
    # The encoded pw is BITS datatype once encrypted and needs it's own variable
    list_pw.append([new_acct, new_username, encoded_pw.decode()])

    # Return to home or repeat
    again = str(input(line + mode + another))
    if again.lower() == "y":
        add_pw()
    else:
        start()


# Edit a password from the encrypted passwords list based on it's index
def edit_pw():
    mode = "Edit"
    print(line)
    place = 1
    for i in list_pw:
        print(place, i[0])
        place += 1

    index = int(int(input(line + select + mode.lower() + typing)) - 1)

    replace_pw = str(input("New Password: "))
    # User input value for replace_pw is encoded then saved to a new variable
    replace_encoded_pw = fernet.encrypt(replace_pw.encode())
    # Issues arise when assigning the value directly to the sub-list index
    # To avoid this we first remove the last value in the relevant sub-list
    # Then append the decoded variable to the relevant sub-list
    # Remember the value needs to be decoded before adding to the encrypted passwords list
    # This converts the values datatype from BITS to STRING
    list_pw[index].remove(list_pw[index][-1])
    list_pw[index].append(replace_encoded_pw.decode())

    # Return to home or repeat
    again = str(input(line + mode + another))
    if again.lower() == "y":
        edit_pw()
    else:
        start()


# Remove a password from the encrypted passwords list based on it's index
def del_pw():
    mode = "Delete"
    print(line)
    place = 1
    for i in list_pw:
        print(place, i[0])
        place += 1

    index = int(int(input(line + select + mode.lower() + typing)) - 1)

    # Check if the user wants to delete the chosen pw
    sure = str(input(f"{line}Are you sure you want to delete the password for {list_pw[index][0]} ?{yes_no}"))
    if sure.lower() == "y":
        list_pw.remove(list_pw[index])
    elif sure.lower() == "n":
        start()

    # Return to home or repeat
    again = str(input(line + mode + another))
    if again.lower() == "y":
        del_pw()
    else:
        start()


# Choose a password to display based on it's index in the encrypted passwords list
def show_pw():
    mode = "Decrypt"
    print(line)
    place = 1
    for i in list_pw:
        print(place, i[0])
        place += 1

    index = int(int(input(line + select + mode.lower() + typing)) - 1)

    # Similar to encrypting, the decrypted password needs to be stored in a new variable
    decoded_pw = fernet.decrypt(list_pw[index][-1])
    # Remember to decode the new variable to remove the leading b value
    # This changes b'variable' to 'variable'
    print(decoded_pw.decode())

    # Return to home or repeat
    again = str(input(line + mode + another))
    if again.lower() == "y":
        show_pw()
    else:
        start()

# Temp run app in terminal while figuring out basic tkinter
# Possiblly make a cli version of app and gui? Give the user the option ?
start()

# # Create the root frame window thing with tkinter and initialize the app - read more docs
# root = tk.Tk()
# root.title("Simple Password Manager")

# # Run the app
# root.mainloop()
