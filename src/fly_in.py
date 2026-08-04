from menu import Menu
import sys

if __name__ == "__main__":
    menu = Menu()
    try:
        menu.display_all_menu()
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt error")
        sys.exit(0)
