import os
from subprocess import call
from typing import Any

from pydantic import BaseModel, Field, ValidationError, model_validator


class HubModel(BaseModel):
    """Pydantic model representing a hub.

    Attributes:
        name (str): Unique name of the hub.
        x (int): X-coordinate position on the map.
        y (int): Y-coordinate position on the map.
        occupancy (int): Current number of drones occupying the hub.
        reserved_drones (int): Number of drones reserved for this hub.
        metadata (dict[str, Any]): Additional hub parameters and metadata.
    """

    name: str
    x: int
    y: int
    occupancy: int
    metadata: dict[str, Any]

    @model_validator(mode="after")
    def validate_data(self) -> "HubModel":
        """Validates that the hub name does not contain illegal characters.

        Returns:
            HubModel: Validated hub instance.
        """
        if "-" in self.name:
            raise ValueError("Dash are not accepted in name zone")
        return self


class ConnectionModel(BaseModel):
    """Pydantic model representing a connection between two hubs.

    Attributes:
        zone1 (str): Name of the first hub.
        zone2 (str): Name of the second hub.
        metadata (dict[str, Any]): Connection properties and limits.
    """

    zone1: str
    zone2: str
    metadata: dict[str, Any]

    @model_validator(mode="after")
    def validate_data(self) -> "ConnectionModel":
        """Validates connected zone names for invalid characters.

        Returns:
            ConnectionModel: Validated connection instance.
        """
        if "-" in self.zone1 or "-" in self.zone2:
            raise ValueError("Dash are not accepted in name zone")
        return self


class MapModel(BaseModel):
    """Pydantic model representing a complete map configuration.

    Attributes:
        name (str): Name of the map.
        drones (int): Total number of drones operating on the map.
        start_hub (HubModel): Starting point hub.
        end_hub (HubModel): Destination hub.
        hubs (list[HubModel]): Intermediate hubs.
        connections (list[ConnectionModel]): Connections between hubs.
    """

    name: str
    drones: int = Field(ge=1)
    start_hub: HubModel
    end_hub: HubModel
    hubs: list[HubModel] = Field(default_factory=list)
    connections: list[ConnectionModel] = Field(default_factory=list)


class ParsingError(Exception):
    """Exception raised when a line-specific error occurs during map parsing.

    Attributes:
        line_num (int): Line number where the error occurred.
        message (str): Detailed error description.
    """

    def __init__(self, line_num: int, message: str) -> None:
        """Initializes ParsingError with line number and message.

        Args:
            line_num (int): Line number associated with the error.
            message (str): Error description message.
        """
        self.line_num = line_num
        self.message = message
        super().__init__(f"Line {line_num}: {message}")


class Parser:
    """Parses map files into structured MapModel objects.

    Attributes:
        data (MapModel): Parsed map data object.
        seen_hub_names (set[str]): Collection of unique parsed hub names.
        seen_connections (set[tuple[str, str]]): Set of recorded connections.
    """

    def __init__(self, file: str) -> None:
        """Initializes the parser and triggers map file parsing.

        Args:
            file (str): Path to the map configuration file.
        """
        self._file = file
        self.seen_hub_names: set[str] = set()
        self.seen_connections: set[tuple[str, str]] = set()
        self.data = self._parse_map()

    def read_file(self) -> list[str]:
        """Reads and cleans valid lines from the map file.

        Returns:
            list[str]: Filtered non-empty, non-comment lines.
        """
        with open(self._file) as f:
            call("clear" if os.name == "posix" else "cls")
            lines = [
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]
        return lines

    def _parse_map(self) -> MapModel:
        """Parses the loaded lines into a MapModel object.

        Returns:
            MapModel: Complete parsed map structure.
        """
        lines = self.read_file()
        payload: dict[str, Any] = {
            "name": os.path.basename(self._file).removesuffix(".txt"),
            "nb_drones": None,
            "start_hub": None,
            "end_hub": None,
            "hubs": [],
            "connections": [],
        }
        for line_num, line in enumerate(lines, start=1):
            try:
                key, data = line.split(":", 1)
            except ValueError:
                raise ParsingError(line_num, "Invalid Format")
            if key.lower() == "nb_drones":
                if payload["nb_drones"] is not None:
                    raise ParsingError(
                        line_num, "Duplicate 'nb_drones' definition"
                    )
                if line_num > 1:
                    raise ParsingError(
                        line_num, "'nb_drones' must be the first instruction"
                    )
                try:
                    value = int(data)
                    if value <= 0:
                        raise ParsingError(
                            line_num, "You need at least 1 drone"
                        )
                    payload["nb_drones"] = value
                except ValueError:
                    raise ParsingError(
                        line_num, "'nb_drones' value must be a valid integer"
                    )
            elif key.lower() == "hub":
                payload["hubs"].append(self._parse_hub(line_num, data, False))
            elif key.lower() == "start_hub":
                if payload["start_hub"] is None:
                    payload["start_hub"] = self._parse_hub(
                        line_num, data, True
                    )
                else:
                    raise ParsingError(
                        line_num, "There must be exactly one start_hub"
                    )
            elif key.lower() == "end_hub":
                if payload["end_hub"] is None:
                    payload["end_hub"] = self._parse_hub(line_num, data, True)
                else:
                    raise ParsingError(
                        line_num, "There must be exactly one end_hub"
                    )
            elif key.lower() == "connection":
                payload["connections"].append(
                    self._parse_connection(line_num, data)
                )
            else:
                raise ParsingError(line_num, "Invalid Format")
        if payload["start_hub"] is None or payload["end_hub"] is None:
            raise ParsingError(
                line_num, "Missing start_hub or end_hub definition"
            )
        try:
            map = MapModel(
                name=payload["name"],
                drones=payload["nb_drones"],
                start_hub=payload["start_hub"],
                end_hub=payload["end_hub"],
                hubs=payload["hubs"],
                connections=payload["connections"],
            )
            return map
        except ValidationError as e:
            raise ValueError(
                f"Error in the file: {self._file}:" f"{e.errors()[0]['msg']}"
            )

    def _parse_hub(self, line_num: int, data: str, type: bool) -> HubModel:
        """Parses line data into a HubModel instance.

        Args:
            line_num (int): Current line number.
            data (str): Raw hub data string.
            type (bool): True if start/end hub (disables max_drones metadata).

        Returns:
            HubModel: Parsed hub instance.
        """
        mandatory, _, optional = data.partition("[")
        left_elements = mandatory.split()
        if len(left_elements) != 3:
            raise ParsingError(line_num, "Invalid Format")
        name, x_str, y_str = left_elements

        if name in self.seen_hub_names:
            raise ParsingError(
                line_num, f"Duplicate hub name: '{name}' detected"
            )
        try:
            name, x, y = name, int(x_str), int(y_str)
        except ValueError:
            raise ParsingError(line_num, "Coordinates must be integer")
        metadata = self.parse_metadata(line_num, optional)
        if type:
            metadata.pop("max_drones", None)
        try:
            hub = HubModel(
                name=name,
                x=x,
                y=y,
                occupancy=0,
                metadata=metadata,
            )
            self.seen_hub_names.add(name)
            return hub
        except ValidationError as e:
            raise ParsingError(line_num, f"{e.errors()[0]['msg']}")

    def _parse_connection(self, line_num: int, data: str) -> ConnectionModel:
        """Parses line data into a ConnectionModel instance.

        Args:
            line_num (int): Current line number.
            data (str): Raw connection data string.

        Returns:
            ConnectionModel: Parsed connection instance.
        """
        mandatory, _, optional = data.partition("[")
        left_elements = mandatory.split("-")
        if len(left_elements) != 2:
            raise ParsingError(line_num, "Invalid Format")
        zone_1, zone_2 = [elem.strip() for elem in left_elements]
        if zone_1 not in self.seen_hub_names:
            raise ParsingError(
                line_num,
                f"Hub name '{zone_1}' not defined, impossible connection",
            )
        if zone_2 not in self.seen_hub_names:
            raise ParsingError(
                line_num,
                f"Hub name '{zone_2}' not defined, impossible connection",
            )
        a, b = sorted((zone_1, zone_2))
        conn: tuple[str, str] = (a, b)
        if conn in self.seen_connections:
            raise ParsingError(
                line_num, f"Duplicate connection: '{conn}' detected"
            )
        try:
            connect = ConnectionModel(
                zone1=zone_1,
                zone2=zone_2,
                metadata=self.parse_metadata(line_num, optional),
            )
            self.seen_connections.add(conn)
            return connect
        except ValidationError as e:
            raise ParsingError(line_num, f"{e.errors()[0]['msg']}")

    def parse_metadata(self, line_num: int, data: str) -> dict[str, Any]:
        """Parses optional key-value metadata bracket string.

        Args:
            line_num (int): Current line number.
            data (str): Metadata string content inside brackets.

        Returns:
            dict[str, Any]: Dictionary of metadata key-value pairs.
        """
        metadata = {}
        valid_metadata = ["zone", "color", "max_link_capacity", "max_drones"]
        zone_types = ["normal", "blocked", "restricted", "priority"]
        right_elements = data.strip("]").split()
        for element in right_elements:
            try:
                key, value = element.split("=", 1)
            except ValueError:
                raise ParsingError(line_num, "Invalid format for metadata")
            if key not in valid_metadata:
                raise ParsingError(
                    line_num, f"Invalid Metadata key: {key} detected"
                )
            if key == "zone":
                if value not in zone_types:
                    raise ParsingError(
                        line_num, f"Invalid zone type: {value} detected"
                    )
            elif key == "max_drones" or key == "max_link_capacity":
                try:
                    val = int(value)
                except ValueError:
                    raise ParsingError(
                        line_num, "Max capacity must be an integer"
                    )
                if val <= 0:
                    raise ParsingError(
                        line_num, "Max capacity needs to be positive integer"
                    )
            metadata[key] = value

        return metadata
