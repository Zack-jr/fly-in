from pydantic import BaseModel, model_validator, ValidationError, Field
from collections import defaultdict
from typing import List
from enum import Enum
from itertools import cycle
import heapq


# ASSIGN A COST TO EACH ZONE_TYPE
# PYDANTIC WILL CONVERT STR INTO ENUM
class ZoneType(Enum):
    normal = 1
    priority = 1
    restricted = 2
    blocked = float('inf')


# ZONE (OR HUB) INSIDE THE GRAPH
# DRONES NAVIGATE THROUGH ZONES
class Zone(BaseModel):
    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.normal
    color: str | None = None
    max_drones: int = 1
    hub_type: str
    current_drones: int = 0

    @model_validator(mode="after")
    def validate_zone(self):
        if self.max_drones < 0:
            raise ValueError(f"Invalid max_drones count: {self.max_drones}.")
        return self

    def get_movement_cost(self):
        return self.zone_type.value

#   CONNECTION (LINKS) BETWEEN ZONES
class Connection(BaseModel):
    zone1: str
    zone2: str
    max_link_capacity: int = 1
    current_drones: int = 0

    @model_validator(mode="after")
    def validate_connection(self):
        if self.max_link_capacity < 0:
            raise ValueError("max_link_capacity cannot be negative")

        return self

# DRONE
# NAVIGATES ZONE BY ZONE
class Drone():
    def __init__(self, drone_id: str):
        self.ID = drone_id
        self.position = ""
        self.path : List[Zone] = []
        self.delivered : bool = False
        self.path_index : int = 0



# ENTIRE GRAPH STRUCTURE
# IS COMPOSED BY ZONES AND CONNECTIONS
# WILL MANAGE THE WHOLE SIMULATION PROCESS
class Graph(BaseModel): 
    zones: dict[str, Zone] = Field(default_factory=dict)
    connections: list[Connection] = Field(default_factory=list)
    drone_count: int = Field(default_factory=int)
    drones: list = Field(default_factory=list, exclude=True)
    adjacency : dict[str, list[Zone]] = Field(default_factory=dict)
    connection_map: dict[tuple[str, str], Connection] = Field(default_factory=dict)
    start_hub: Zone
    end_hub: Zone

    # CHECK FOR VALID NUMBER OF DRONES
    @model_validator(mode="after")
    def validate_graph(self):
        if self.drone_count <= 0:
            raise ValueError("Drone count cannot be less than or equal to 0.")

        self.end_hub.max_drones = self.drone_count
        self.adjacency_maker()
        return self

    def find_paths(self) -> List[str]:
        
        used_zones : set[str] = set()
        paths = []

        # loop until we find the same path twice
        while True:

            path = self.dijkstra(self.start_hub, self.end_hub, used_zones)
            paths_names = [z.name for z in path]
    
            # break if we find the same path twice
            if paths_names in paths:
                break
        
            paths.append(paths_names)
            for zone in paths[1:-1]:
                used_zones.add(zone.name)

        return paths

    # CREATE AND INITIALIZE ZONES IN START HUB POSITION
    def create_drones(self) -> None:

        used_zones : set[str] = set()
        path = self.find_paths()
        path_cycle = cycle(path)

        for i in range(1, self.drone_count + 1):
            self.drones.append(Drone(f"D{i}"))

        #  assign path and position for drones
        # convert string into zone using dict
        for drone in self.drones:
            path_names = next(path_cycle)
            drone.path = [self.zones[name] for name in path_names]
            drone.position = self.start_hub.name
            print(f"{drone.ID} path: {[z.name for z in drone.path]}")

    # GET NEIGHBORING ZONES FOR A SPECIFIC ZONE
    def get_neighbors(self, zone) -> list[Zone]:
        return self.adjacency[zone.name]

    # CREATES DICTS WITH NEIGHBORING ZONES FOR EASY LOOKUP
    def adjacency_maker(self) -> None:

        # automatically initializes keys
        adjacency_dict = defaultdict(list)
        connection_dict : dict[tuple[str, str], Connection] = {}

        # loop through the connections to create a dict of node: neighboring nodes
        # and a dict of connections
        for connection in self.connections:
            adjacency_dict[connection.zone1].append(self.zones[connection.zone2])
            adjacency_dict[connection.zone2].append(self.zones[connection.zone1])
            key = tuple(sorted([connection.zone1, connection.zone2]))
            connection_dict[key] = connection

        self.adjacency = adjacency_dict
        self.connection_map = connection_dict


    # SIMULATE DRONE ROUTE
    def simulate(self) -> None:

        turn_count = 0
        turn_movements = ""
        self.create_drones()

        # while the drones are not all delivered
        while not all(drone.delivered for drone in self.drones):


            # set every connection drone count to 0 every turn
            for conn in self.connections:
                conn.current_drones = 0
            # for every drone
            for drone in self.drones:
                
                # if it's delivered -> skip
                if drone.delivered:
                    continue

                previous_zone = drone.path[drone.path_index]
                next_zone = drone.path[drone.path_index + 1]

                # get connection dict access by reference
                key = tuple(sorted([previous_zone.name, next_zone.name]))
                connection = self.connection_map[key]

                # if the next zone has the capacity and the connection allows it
                if (connection.current_drones < connection.max_link_capacity
                    and next_zone.current_drones < next_zone.max_drones):
                    connection.current_drones += 1
                    drone.position = next_zone.name
                    drone.path_index += 1
                    next_zone.current_drones += 1
                    previous_zone.current_drones -= 1
                    turn_movements += (f"{drone.ID}-{drone.position} ")

                    if drone.position == self.end_hub.name:
                        drone.delivered = True

                # NEED TO HANDLE CONNECTIONS
                else:
                    continue

            print(turn_movements)
            turn_count += 1
            turn_movements = ""
        print(f"Number of turns: {turn_count}\n")

    # FINDS SHORTEST PATH FROM ENTRY TO EXIT
    def dijkstra(self, start : Zone, end: Zone, used_zones: set[str] | None) -> List[Zone]:

        distances = {}
        path = []
        heap = [(0, start.name)]
        came_from : dict[str, str] = {}

        if used_zones is None:
            used_zones = set()
            
        # ASSIGN A COST TO EACH DISTANCE
        for name in self.zones.keys():
            distances[name] = float('inf')

        # STARTING ZONE IS 0 COST
        distances[start.name] = 0

        while heap:
            current_cost, current_name = heapq.heappop(heap)

            # if we reached the end
            if current_name == end.name:
                break

            # for every neighbor of the current zone
            for neighbor in self.adjacency[current_name]:
        
                # skip this iteration if zone is blocked
                if neighbor.zone_type == ZoneType.blocked:
                    continue

                # get cost for movement to neighbor
                new_cost = current_cost + neighbor.get_movement_cost()
                if neighbor.name in used_zones:
                    new_cost += 1

                # if new cost is better than previous cost
                if new_cost < distances[neighbor.name]:
                    distances[neighbor.name] = new_cost
                    heapq.heappush(heap, (new_cost, neighbor.name))
                    came_from[neighbor.name] = current_name


        # CHECK IF THE END HAS BEEN FOUND AND IS IN THE KEYS
        if end.name not in came_from:
            raise ValueError(f"No path found from {start.name} to {end.name}")

        #PATH RECONSTRUCTION
        current = end

        while current.name != start.name:
            path.append(current)
            current = self.zones[came_from[current.name]]

        path.append(start)
        path.reverse()

        return path

#   - Don't release all drones at once
#   - Send them gradually(avoid congestion)

# Paths -> Assign -> Simulate with constraints