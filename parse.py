#!/usr/bin/env python3

import os
import sys
from models import (
        Hub, 
        Map, 
        Metadata, 
        ZoneType, 
        FileKeys, 
        MetaKeys, 
        Connection
        )
from typing import TypedDict
from exceptions import ParseError


class MapBuilder():
    def __init__(self, data: dict[str, list[str]]) -> None:
        self._data = data

        for key in ("nb_drones", "start_hub", "end_hub"):
            if key not in self._data or len(self._data[key]) != 1:
                raise ParseError(f"Expected exactly one '{key}'")

        self._nb_drones = int(self._data["nb_drones"][0])
        self._start_hub = self._build_hub(self._data["start_hub"][0])
        self._end_hub = self._build_hub(self._data["end_hub"][0])
        self._hubs: list[Hub] = []

        if "hub" in self._data:
            for hub in self._data["hub"]:
                new_hub = self._build_hub(hub)

                if new_hub.name in (
                    self._start_hub.name,
                    self._end_hub.name
                ) or any(h.name == new_hub.name for h in self._hubs):
                    raise HubError(f"Duplicate hub: (new_hub.name)")
                
                self._hubs.append(new_hub)
        
        if not "connection" in self._data:
            raise ParseError("Connection information must exist")

        self._connections: list[Connection] = []
        for connection in self._data["connection"]:
            new_connection = self._build_connection(connection)

            for existing in self._connections:
                if (existing.hub1.name, existing.hub2.name) == {
                    new_connection.hub1.name,
                    new_connection.hub2.name
                    }:
                    raise ConnectionsError("Duplicate connection")

            self._connections.append(new_connection)

    def get_map(self) -> Map:

        return Map(
                nb_drones=self._nb_drones,
                start=self._start_hub,
                end=self._end_hub,
                hubs=self._hubs,
                connections=self._connections
                )

    def _build_metadata(self, data: list[str]) -> Metadata:
        metas: dict[str, str] = {}

        if len(data) > 3:
            split_metadata = data[3:]
            
            for meta in split_metadata:
                k = meta.replace("[", "").replace("]", "").split("=")
                if k[0] not in MetaKeys:
                    raise ParseError(f"Metadata type error: {k[0]}"
                                     " is not a valid meta type"
                    )
                if len(k) != 2:
                    raise ParseError("Invalid metadata format")
                    
                metas[k[0]] = k[1]

        zone = ZoneType(metas.get("zone", "normal"))
        color = metas.get("color")
        max_drones = int(metas.get("max_drones", "1"))

        return Metadata(
            zone=zone,
            color=color,
            max_drones=max_drones
        )

    def _build_hub(self, data: str) -> Hub:
        split_data = data.split()
        
        if len(split_data) < 3:
            raise ParseError("Hub must contain name and coordinates")

        name, x, y = split_data[:3]

        return Hub(name=name,
                   coordinates=(int(x), int(y)),
                   metadata=self._build_metadata(split_data)
                  )

    def _build_connection(self, data: str) -> Connection:
        s_hubs = data.replace("-", " ").split()

        if len(s_hubs) != 2 and len(s_hubs) != 3:
            raise ParseError(f"A connection must be between two hubs")

        hubs: list[Hub] = []
        for name in s_hubs[:2]: 
            name = name.strip()

            if name == self._start_hub.name:
                hubs.append(self._start_hub)
            elif name == self._end_hub.name:
                hubs.append(self._end_hub)
            else:
                hub = next((hub for hub in self._hubs if hub.name == name),
                            None)
                if hub is None:
                    print(s_hubs)
                    raise ParseError(f"Hub not found: {name}")
                hubs.append(hub)

        link = 1
        if len(s_hubs) == 3:
            metadata = s_hubs[2].strip("[]").split("=")
            
            if len(metadata) != 2 or metadata[0] != "max_link_capacity":
                raise ConnectionsError("Invalid connection metadata")

            link = int(metadata[1])

        return Connection(hubs[0], hubs[1], link_capacity=link)


def get_file() -> dict[str, list[str]]:

    if len(sys.argv) < 2:
        raise ParseError("Missing filename")

    filename = sys.argv[1]
    data: dict[str, list[str]] = {}
    if os.path.exists(filename):
        with open(filename, "r") as file:
            content = file.read()

            for line in content.splitlines():
                if line.strip().startswith("#") or not line.strip():
                    continue

                kv: list[str] = line.split(":")

                if not kv[0] in FileKeys:
                    raise ParseError(f"Key format not acepted for {kv[0]}")
                else:
                    data.setdefault(kv[0], []).append(kv[1])
                    
        return data

    else:
        raise FileNotFoundError(f"File not found: {filename}")


def main() -> None:
    data = get_file()
    builder = MapBuilder(data)
    my_map = builder.get_map()

    print(my_map)


if __name__ == "__main__":
    main()
