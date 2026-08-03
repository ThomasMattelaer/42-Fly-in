from simple_term_menu import TerminalMenu  # type: ignore
from parser import Parser
import os


class Menu():
    def start(self, options: list[str]) -> str:
        terminal_menu = TerminalMenu(
            options,
            title="Please select a map:",
            clear_screen=True,
            raise_error_on_interrupt=True,
            menu_cursor="-> ",
            menu_cursor_style=("fg_blue", "bold"),
            menu_highlight_style=("bg_purple", )
        )
        entry_index = terminal_menu.show()
        result = options[entry_index]
        return result

    def list_files(self, directory: str) -> list[str]:
        files = [file for file in os.listdir(directory)]
        is_root_maps = os.path.abspath(directory) == os.path.abspath("./maps")
        return files if is_root_maps else files + ["back"]

    def display_all_menu(self, initial_directory: str = "./maps") -> None:
        current_path: str = initial_directory
        print(f"current : {current_path}, dir: {os.path.isdir(current_path)}")
        while (os.path.isdir(current_path)):
            result = self.start(self.list_files(current_path))
            if result == "back":
                current_path = os.path.dirname(current_path)
            else:
                current_path = os.path.join(current_path, result)
        if (os.path.isfile(current_path)):
            Parser(current_path)
