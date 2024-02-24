# Tkinter packages for GUI
from tkinter import *
from tkinter import Menu
from tkinter.ttk import *
# Ttkbootstrap for styling
import ttkbootstrap as ttk
from ttkbootstrap.constants import *



# Create the mainWindow and styling
mainWindow = ttk.Window(title="Web App Deployer", size=(500, 600), themename="superhero")



# Create the Optionmenu variable and set to blank
webapp = StringVar()
webapp.set("Select Web App to Deploy")
# List available web apps to deploy in the Optionmenu
options = ["Select Web App to Deploy", "Web Service", "Web Logger"]
OptionMenu(mainWindow, webapp, *(options)).pack(side=TOP, padx=5, pady=10)


# List of requiredDetails with labels and entry widgets
requiredDetails = ['Server Name', 'Database Name']
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
testingButton = ttk.Button(mainWindow, text="Deploy", bootstyle=PRIMARY)
testingButton.pack(side=TOP, padx=5, pady=10)
# Quit button sends command to destroy mainWindow
quitButton = ttk.Button(mainWindow, text="Quit", bootstyle=DANGER, command=mainWindow.destroy)
quitButton.pack(side=TOP, padx=5, pady=10)



# Start the program using the mainWindow
#mainWindow.mainloop()