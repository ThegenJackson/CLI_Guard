import readchar
import os
from colorama import init, Fore, Back, Style

# Initialize Colorama (autoreset restores default after print)
init(autoreset=True)

options = ["Option 1", "Option 2", "Option 3", "Exit"]
selected_index = 0

def display_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.CYAN}Use ↑ and ↓ to navigate. Press Enter to select.{Style.RESET_ALL}\n")
    for i, option in enumerate(options):
        if i == selected_index:
            print(f"{Back.WHITE}{Fore.BLACK}{option}{Style.RESET_ALL}")  # Highlight current option
        else:
            print(option)

while True:
    display_menu()
    key = readchar.readkey()

    if key == readchar.key.UP:
        selected_index = (selected_index - 1) % len(options)
    elif key == readchar.key.DOWN:
        selected_index = (selected_index + 1) % len(options)
    elif key == readchar.key.ENTER:
        print(f"You selected: {options[selected_index]}")
        if options[selected_index] == "Exit":
            break
