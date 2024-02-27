# Send commands to the Command Prompt
import os

# If Administrator is needed at Command Prompt
# subprocess.call(['runas', '/user:Administrator', 'Your command'])
import subprocess

# Interact with IIS
import iis_bridge

# Tkinter packages for GUI
from tkinter import *
from tkinter import Menu
from tkinter.ttk import *
# Ttkbootstrap for styling
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


def testing():
        # Intermediary list helps to split the details for later use we can refer to the list index
        # Not using the intermediary list seems to introduce issues
        details = []
        # Looping through the entries list was the simplest method to overcome consistent errors with other approaches
        for entry in entries:
            # Use .get() to pull values from the Tkinter Entry widget
            value = entry.get()
            # .strip() the Entry widget value of any leading spaces then skip any entry in entries that == an empyty string
            if value.strip() == '':
                continue
            else:
                # Non-empty strings are stripped of leading spaces then appended to details list
                details.append(value.strip())

        # Check if all fields are populated, does the number of details submitted == number of details required
        if len(details) == len(requiredDetails):
            account = details[0]
            username = details[1]
            password = details[-1]

            print(account, username, password)
        else:
            print("1 or more required details are missing")


# Create the mainWindow and styling
mainWindow = ttk.Window(title="Simple Password Manager", size=(1200, 600), themename="superhero")


# List of requiredDetails with labels and entry widgets
requiredDetails = ['Account', 'Username', 'Password']
# List of requiredDetails values
entries = []
# Add labels and entry widgets for all requiredDetails and pack into the mainWindow
for detail in requiredDetails:
    label = ttk.Label(mainWindow, text=f"{detail}: ")
    label.pack(side=TOP, anchor=W,  padx=5, pady=10)
    entry = ttk.Entry(mainWindow, style=DEFAULT)
    entry.pack(side=TOP, anchor=W,  padx=5, pady=10)
    entries.append(entry)


# Currently for testing
testingButton = ttk.Button(mainWindow, text="TESTING", bootstyle=PRIMARY, command=testing)
testingButton.pack(side=TOP, anchor=W,  padx=5, pady=10)
# Quit button sends command to destroy mainWindow
quitButton = ttk.Button(mainWindow, text="Quit", bootstyle=DANGER, command=mainWindow.destroy)
quitButton.pack(side=TOP, anchor=W, padx=5, pady=10)



# Start the program using the mainWindow
mainWindow.mainloop()