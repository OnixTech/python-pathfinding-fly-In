from enum import Enum


class ZoneType(str, Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class FileKeys(str, Enum):
    NB_DRONES = "nb_drones"
    START_HUB = "start_hub"
    END_HUB = "end_hub"
    HUB = "hub"
    CONNECTION = "connection"


class MetaKeys(str, Enum):
    ZONE = "zone"
    COLOR = "color"
    MAX_DRONES = "max_drones"


class Metadata:
    def __init__(
        self,
        zone: ZoneType = ZoneType.NORMAL,
        color: str | None = None,
        max_drones: int = 1,
    ) -> None:
        self.zone = zone
        self.color = color
        self.max_drones = max_drones
        self._validation()

    def _validation(self) -> None:
        
        if not isinstance(self.zone, ZoneType):
            raise ValueError(
                f"ZoneType error: {self.zone} is not a valid zone type"
            )

        if type(self.max_drones) is not int or self.max_drones <= 0:
            raise ValueError("max_drones must be a positive integer")


class Hub:
    def __init__(
        self,
        name: str,
        coordinates: tuple[int, int],
        metadata: Metadata | None = None,
    ) -> None:
        self.name = name
        self.coordinates = coordinates
        self.metadata = metadata if metadata is not None else Metadata()
        self._validation()

    def _validation(self) -> None:

        if not self.name or " " in self.name or "-" in self.name:
            raise ValueError(f"Invalid hub name: {self.name}")

        if (
            not isinstance(self.coordinates, tuple)
            or len(self.coordinates) != 2
            or any(type(value) is not int for value in self.coordinates)
        ):
            raise ValueError("Coordinates must contain two integers")


class Connection:
    def __init__(
        self,
        hub1: str,
        hub2: str,
        link_capacity: int = 1,
    ) -> None:
        self.hub1 = hub1
        self.hub2 = hub2
        self.link_capacity = link_capacity
        
        if type(self.link_capacity) is not int or link_capacity <= 0:
            raise ValueError("link_capacity must be positive integer")


class Map:
    def __init__(
        self, 
        nb_drones: int,
        start: Hub,
        end: Hub,
        hubs: list[Hub],
        connections: list[Connection]
    ) -> None:
        self.nb_drones = nb_drones
        self.start = start
        self.end = end
        self.hubs = hubs
        self.connections = connections

        if type(self.nb_drones) is not int or nb_drones <= 0:
            raise ValueError("nb_drones must be positive integer")
