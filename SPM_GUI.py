# Simple Password Manager Graphic User Interface

# Import SPM Python packages
from SPM import *
from SPM import encrypt_pw, decrypt_pw, query_data, insert_data, update_data, delete_data

# Tkinter packages for GUI
from tkinter import *
from tkinter import Menu
from tkinter.ttk import *
# Ttkbootstrap for styling
import ttkbootstrap as ttk
from ttkbootstrap.constants import *



# Create the mainWindow and styling
mainWindow = ttk.Window(title="Simple Password Manager", size=(500, 600), themename="superhero")



# Create the Optionmenu variable and set to blank
testing = StringVar()
testing.set("Select Password")
# List available web apps to deploy in the Optionmenu
options = ["Select Password", "Test", "Testing"]
OptionMenu(mainWindow, testing, *(options)).pack(side=TOP, padx=5, pady=10)


# List of requiredDetails with labels and entry widgets
requiredDetails = ['Account', 'Password']
# List of requiredDetails values
entries = []
# Add labels and entry widgets for all requiredDetails and pack into the mainWindow
for detail in requiredDetails:
    label = ttk.Label(mainWindow, text=f"{detail}: ")
    label.pack(side=TOP, padx=5, pady=10)
    entry = ttk.Entry(mainWindow, style=DEFAULT)
    entry.pack(side=TOP, padx=5, pady=10)
    entries.append(entry)


# Currently for testing
testingButton = ttk.Button(mainWindow, text="Button", bootstyle=PRIMARY)
testingButton.pack(side=TOP, padx=5, pady=10)

# Quit button sends command to destroy mainWindow
quitButton = ttk.Button(mainWindow, text="Quit", bootstyle=DANGER, command=mainWindow.destroy)
quitButton.pack(side=TOP, padx=5, pady=10)


# Call guiStart function from SPM Launcher
def guiStart():
    # Start the program using the mainWindow
    mainWindow.mainloop()



# Start the CLI app
guiStart()