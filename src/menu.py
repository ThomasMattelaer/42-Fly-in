import os
import sys
from parser import MapModel, Parser
from simple_term_menu import TerminalMenu  # type: ignore


class Menu:
    """Interactive terminal menu for selecting and loading map files."""

    def start(self, options: list[str]) -> str:
        """Displays a terminal selection menu and returns the chosen option.

        Args:
            options (list[str]): List of menu entry labels to display.

        Returns:
            str: Selected option label.
        """
        terminal_menu = TerminalMenu(
            options,
            title="Please select a map:",
            clear_screen=True,
            raise_error_on_interrupt=True,
            menu_cursor="-> ",
            menu_cursor_style=("fg_blue", "bold"),
            menu_highlight_style=("bg_purple",),
        )
        entry_index = terminal_menu.show()
        result = options[entry_index]
        return result

    def list_files(self, directory: str) -> list[str]:
        """Lists files in a directory.

        Args:
            directory (str): Path of the directory to list.

        Returns:
            list[str]: File names and navigation choices.
        """
        files = [file for file in os.listdir(directory)]
        is_root_maps = os.path.abspath(directory) == os.path.abspath("./maps")
        return files if is_root_maps else files + ["back"]

    def select_map_menu(self, initial_directory: str = "./maps") -> MapModel:
        """Navigates via terminal menus to select and parse a map file.

        Args:
            initial_directory (str, optional): Defaults to "./maps".

        Returns:
            MapModel: Parsed map data object.
        """
        current_path: str = initial_directory
        while os.path.isdir(current_path):
            result = self.start(self.list_files(current_path))
            if result == "back":
                current_path = os.path.dirname(current_path)
            else:
                current_path = os.path.join(current_path, result)
        if os.path.isfile(current_path):
            try:
                parser = Parser(current_path)
                map_data: MapModel = parser.data
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(0)
        return map_data
