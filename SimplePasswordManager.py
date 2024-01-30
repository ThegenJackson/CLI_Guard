# Import Python Cryptography library and Fernet module according to documentation
import cryptography
from cryptography.fernet import Fernet


# Required for encryption with Fernet as per documentation
key = Fernet.generate_key()
fernet = Fernet(key)

# Create empty list of encrypted passwords
list_pw = []


# Program Start - User chooses function
def start():
    print("Simple Password Manager\nSelect an option:")
    print("1. Create new password\n2. Edit a password\n3. Delete a password\n4. Display a password\n5. Exit\n")
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
        print("Choose by typing a number between 1 and 4")
        start()


# User inputs a password which is encrypted then added to the encrypted passwords list
def add_pw():
    new_acct = str(input("Account: "))
    new_username = str(input("Username: "))
    new_pw = str(input("Password: "))
    encoded_pw = fernet.encrypt(new_pw.encode())
    list_pw.append([new_acct, new_username, encoded_pw.decode()])

    again = str(input("Add another password?\nType Y for Yes or N for No\n(y/n)\n"))
    if again == "Y" or again == "y":
        add_pw()
    elif again == "N" or again == "n":
        start()


# Edit a password from the encrypted passwords list based on it's index
def edit_pw():
    sorted_list = sorted(list_pw)
    print(sorted_list)
    index = int(input("Select a password to edit by typing the index: "))
    replace_pw = str(input("New Password: "))
    replace_encoded_pw = fernet.encrypt(replace_pw.encode())
    list_pw[index].remove(list_pw[index][-1])
    list_pw[index].append(replace_encoded_pw.decode())

    again = str(input("Edit another password?\nType Y for Yes or N for No\n(y/n)\n"))
    if again == "Y" or again == "y":
        edit_pw()
    elif again == "N" or again == "n":
        start()


# Remove a password from the encrypted passwords list based on it's index
def del_pw():
    sorted_list = sorted(list_pw)
    print(sorted_list)
    index = int(input("Select a password to delete by typing the index: "))
    list_pw.remove(list_pw[index])

    again = str(input("Remove another password?\nType Y for Yes or N for No\n(y/n)\n"))
    if again == "Y" or again == "y":
        del_pw()
    elif again == "N" or again == "n":
        start()


# Choose a password to display based on it's index in the encrypted passwords list
def show_pw():
    sorted_list = sorted(list_pw)
    print(sorted_list)
    index = int(input("Select a password to decrypt by typing the index: "))
    decoded_pw = fernet.decrypt(list_pw[index][-1])
    print(decoded_pw.decode())

    again = str(input("Decrypt another password?\nType Y for Yes or N for No\n(y/n)\n"))
    if again == "Y" or again == "y":
        show_pw()
    elif again == "N" or again == "n":
        start()


# Start the program
start()
