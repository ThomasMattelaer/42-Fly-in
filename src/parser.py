from subprocess import call
from typing import Any
from pydantic import BaseModel, Field, ValidationError, model_validator
import os


class HubModel(BaseModel):
    name: str
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    metadata: dict[str, Any]

    @model_validator(mode='after')
    def validate_data(self) -> "HubModel":
        if "-" in self.name:
            raise ValueError("Dash are not accepted in name zone")
        return self


class ConnectionModel(BaseModel):
    zone1: str
    zone2: str
    metadata: dict[str, str]

    @model_validator(mode='after')
    def validate_data(self) -> "ConnectionModel":
        if "-" in self.zone1 or "-" in self.zone2:
            raise ValueError("Dash are not accepted in name zone")
        return self


class MapModel(BaseModel):
    name: str
    drones: int = Field(ge=1)
    start_hub: HubModel
    end_hub: HubModel
    hubs: list[HubModel] = Field(default_factory=list)
    connections: list[ConnectionModel] = Field(default_factory=list)


class Parser():
    def __init__(self, file: str) -> None:
        self._file = file
        self.data = self._parse_map()

    def read_file(self) -> list[str]:
        with open(self._file) as f:
            call('clear' if os.name == 'posix' else 'cls')
            lines = [line.strip() for line in f if line.strip()
                     and not line.strip().startswith('#')]
        return lines

    def _parse_map(self) -> MapModel:
        lines = self.read_file()
        payload: dict[str, Any] = {
            "name": os.path.basename(self._file).removesuffix('.txt'),
            "nb_drones": None,
            "start_hub": None,
            "end_hub": None,
            "hubs": [],
            "connections": []
        }
        for line in lines:
            key, data = line.split(":", 1)
            if key.lower() == "nb_drones":
                payload["nb_drones"] = int(data)
            elif key.lower() == "hub":
                payload["hubs"].append(self._parse_hub(data))
            elif key.lower() == "start_hub":
                if payload["start_hub"] is None:
                    payload["start_hub"] = self._parse_hub(data)
                else:
                    raise ValueError("There must be exactly one start_hub")
            elif key.lower() == "end_hub":
                if payload["end_hub"] is None:
                    payload["end_hub"] = self._parse_hub(data)
                else:
                    raise ValueError("There must be exactly one end_hub")
            elif key.lower() == "connection":
                payload["connections"].append(self._parse_connection(data))
        print(payload)
        try:
            return MapModel(
                name=payload["name"],
                drones=payload["nb_drones"],
                start_hub=payload["start_hub"],
                end_hub=payload["end_hub"],
                hubs=payload["hubs"],
                connections=payload["connections"]
            )
        except ValidationError as e:
            raise ValueError(f"Error in the file: {self._file}:"
                             f"{e.errors()[0]['msg']}")

    def _parse_hub(self, data: str) -> HubModel:
        mandatory, _, optional = data.partition("[")
        left_elements = mandatory.split()
        if len(left_elements) != 3:
            raise ValueError("Invalid Format")
        name, x_str, y_str = left_elements
        name, x, y = name, int(x_str), int(y_str)
        return HubModel(
            name=name,
            x=x,
            y=y,
            metadata=self.parse_metadata(optional)
        )

    def _parse_connection(self, data: str) -> ConnectionModel:
        mandatory, _, optional = data.partition("[")
        left_elements = mandatory.split("-")
        if len(left_elements) != 2:
            raise ValueError("Invalid Format")
        zone_1, zone_2 = left_elements
        return ConnectionModel(
            zone1=zone_1,
            zone2=zone_2,
            metadata=self.parse_metadata(optional)
        )

    def parse_metadata(self, data: str) -> dict[str, str]:
        metadata = {}
        right_elements = data.strip("]").split()
        for element in right_elements:
            key, value = element.split("=", 1)
            metadata[key] = value
        return metadata
