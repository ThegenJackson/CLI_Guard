# Simple Password Manager GUI

# Tkinter packages for GUI
from tkinter import *
from tkinter import Menu
from tkinter.ttk import *
# Ttkbootstrap for styling
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from SimplePasswordManager import *


def testing():
        # # Intermediary list helps to split the details for later use we can refer to the list index
        # # Not using the intermediary list seems to introduce issues
        # details = []
        # # Looping through the entries list was the simplest method to overcome consistent errors with other approaches
        # for entry in entries:
        #     # Use .get() to pull values from the Tkinter Entry widget
        #     value = entry.get()
        #     # .strip() the Entry widget value of any leading spaces then skip any entry in entries that == an empyty string
        #     if value.strip() == '':
        #         continue
        #     else:
        #         # Non-empty strings are stripped of leading spaces then appended to details list
        #         details.append(value.strip())

        # # Check if all fields are populated, does the number of details submitted == number of details required
        # if len(details) == len(requiredDetails):
        #     username = details[0]
        #     password = details[-1]

        #     print(username, password)
        # else:
            print("testing")


# Create the loginWindow and styling
loginWindow = ttk.Window(title="Simple Password Manager", size=(300, 400), themename="superhero")

list_master = query_data("users")
# Check if list_master is empty
if list_master != []:

    # List of requiredDetails with labels and entry widgets
    requiredDetails = ['Username:', 'Password:']
    # List of requiredDetails values
    entries = []
    # Add labels and entry widgets for all requiredDetails and pack into the loginWindow
    for detail in requiredDetails:
        label = ttk.Label(loginWindow, text=f"{detail}: ")
        label.pack(side=TOP, anchor=W,  padx=5, pady=10)
        entry = ttk.Entry(loginWindow, style=DEFAULT)
        entry.pack(side=TOP, anchor=W,  padx=5, pady=10)
        entries.append(entry)


    # Currently for testing
    testingButton = ttk.Button(loginWindow, text="Log In", bootstyle=PRIMARY, command=testing)
    testingButton.pack(side=TOP, anchor=W,  padx=5, pady=10)
    # Quit button sends command to destroy loginWindow
    quitButton = ttk.Button(loginWindow, text="Quit", bootstyle=DANGER, command=loginWindow.destroy)
    quitButton.pack(side=TOP, anchor=W, padx=5, pady=10)
else:
    # Currently for testing
    testButton = ttk.Button(loginWindow, text="Create new user", bootstyle=PRIMARY, command=testing)
    testButton.pack(padx=5, pady=10)
    # Quit button sends command to destroy loginWindow
    quitButton = ttk.Button(loginWindow, text="Quit", bootstyle=DANGER, command=loginWindow.destroy)
    quitButton.pack(padx=5, pady=10)



# Start the program using the loginWindow
#loginWindow.mainloop()