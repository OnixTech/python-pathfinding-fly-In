#!/usr/bin/env python3

import os
import sys
from models import Hub, Map, Metadata, ZoneType, FileKeys, MetaKeys, Connection
from enum import Enum
from typing import TypedDict


class MapBuilder():
    def __init__(self, data: dict[str, list[str]]) -> None:
        self._data = data
#        self.map: Map = self._build_map()
        self._build_map()

    def _build_map(self): # -> Map:
        nb_drones = int(self._data["nb_drones"][0])
        start_hub = self._build_hub(data=self._data["start_hub"][0])
        end_hub = self._build_hub(data=self._data["end_hub"][0])
        hubs: list[Hub] = []
        connections: list[Connection] = []

        print(nb_drones, start_hub, end_hub)
#         for k, v in self._data:
#             if k == "hub":
#                 hubs.append(self._build_hub(k, v[0]))
# 
#             if k == "connection":
#                 connections.append(self_build_connection(v[0]))
# 
#         return {
#             "nb_drones": int(self._data["nb_drones"][0]),
#             "start_end": [
#                 Hub(start[0], s_xy, start[3]),
#                 Hub(end[0], e_xy, end[3])
#             ],
#             "connections": [],
#         }

    def _build_metadata(self, data: list[str]) -> Metadata:
        metas: dict[str, str] = {}

        if len(data) > 3:
            split_metadata = data[3:]
            
            for meta in split_metadata:
                k = meta.replace("[", "").replace("]", "").split("=")
                if k[0] not in MetaKeys:
                    raise ValueError(f"Metadata type error: {k[0]}"
                                     " is not a valid meta type"
                    )
                if len(k) != 2:
                    raise ValueError("Invalid metadata format")
                    
                metas[k[0]] = k[1]

        args: MetadataArgs = {}

        if "zone" in metas:
            args["zone"] = ZoneType(metas["zone"])

        if "color" in metas:
            args["color"] = metas["color"]

        if "max_drones" in metas:
            args["max_drones"] = int(metas["max_drones"])

        return Metadata(**args)

    def _build_hub(self, data: str) -> Hub:
        split_data = data.split()
        
        if len(split_data) < 3:
            raise ValueError("Hub must contain name and coordinates")

        name, x, y = split_data[:3]

        return Hub(name=name,
                   coordinates=(int(x), int(y)),
                   metadata=self._build_metadata(split_data)
                  )
    

def get_file() -> MapBuilder:

    if len(sys.argv) < 2:
        raise ValueError("Missing filename")

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
                    raise ValueError(f"Key format not acepted for {kv[0]}")
                else:
                    data.setdefault(kv[0], []).append(kv[1])
                    
        a = MapBuilder(data)            
        return a

    else:
        raise FileNotFoundError(f"File not found: {filename}")


print(get_file())
