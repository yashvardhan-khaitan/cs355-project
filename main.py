import sys
from server import start_server
from client import start_client

def main_menu():
    print("\n")
    print("Welcome!\n")
    print("1. Start an instance for a client to connect to")
    print("2. Connect to an instance of a server")
    print("3. Exit")
    choice = input("\n\nEnter your choice: ")
    return choice
  
if __name__ == "__main__":
    while True:
        choice = main_menu()
        if choice == "1":
            start_server()
        elif choice == "2":
            start_client()
        elif choice == "3":
            sys.exit()
        else:
            print("Invalid choice")