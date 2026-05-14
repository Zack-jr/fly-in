from typing import List, Dict
from pydantic import BaseModel, Field, model_validator
from models.zone import Zone, ZoneType, Colors
from models.connection import Connection
from models.drone import Drone
from collections import defaultdict
from itertools import cycle
import heapq

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

    def find_paths(self) -> List[List[str]]:
        """Generates as many paths as possible in order
        to assign them to n number of drones"""

        # KEEP TRACK OF THE USED ZONES TO ADD
        # A PENALTY SYSTEM TO DIJKSTRA
        used_zones : set[str] = set()
        paths = []

        # LOOP UNTIL WE GENERATE THE SAME PATH TWICE
        while True:

            path = self.dijkstra(self.start_hub, self.end_hub, used_zones)
            paths_names = [z.name for z in path]
    
            # break if we find the same path twice
            if paths_names in paths:
                break
        
            paths.append(paths_names)

            # EXCLUDE FIRST AND LAST ZONES
            # BECAUSE THEY SHOULD NOT BE PENALIZED

            for zone in path[1:-1]:
                used_zones.add(zone.name)

        return paths

    # CREATE AND INITIALIZE ZONES IN START HUB POSITION
    def create_drones(self) -> None:

        # DISTRIBUTE THE PATHS TO THE DRONE
        # WITH A CYCLIC PATTERN

        paths = self.find_paths()
        path_cycle = cycle(paths)

        for i in range(1, self.drone_count + 1):
            self.drones.append(Drone(f"D{i}"))

        #  assign path and position for drones
        # convert string into zone using dict
        for drone in self.drones:
            path_names = next(path_cycle)
            drone.path = [self.zones[name] for name in path_names]
            drone.position = self.start_hub.name


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

            # RESET EVERY TURN
            for conn in self.connections:
                conn.current_drones = 0

            for zone in self.zones.values():
                zone.current_drones = 0

            for drone in self.drones:
                drone.moved_this_turn = False

            # for every drone
            for drone in self.drones:
    
                # if the drone is not delivered
                if not drone.delivered:
                    if drone.in_transit:
                        drone.transit_destination.current_drones += 1
                    else:
                        self.zones[drone.position].current_drones += 1
    
                # if we reached the end for a drone, continue


            for drone in self.drones:

                if drone.delivered or not drone.in_transit or drone.moved_this_turn:
                    continue

                previous_zone = drone.path[drone.path_index]
                next_zone = drone.path[drone.path_index + 1]

                key = tuple(sorted([previous_zone.name, next_zone.name]))
                connection = self.connection_map[key]
    
                if drone.in_transit:
                    connection.current_drones += 1
                    drone.position = drone.transit_destination.name
                    drone.path_index += 1
                    drone.in_transit = False
                    drone.transit_destination = None
                    turn_movements += (f"{drone.ID}-{drone.position} ")

                    if drone.position == self.end_hub.name:
                        drone.delivered = True
                    drone.moved_this_turn = True
            

            for drone in self.drones:
        
                if drone.delivered or drone.in_transit or drone.moved_this_turn:
                    continue
    
                if drone.path_index >= len(drone.path) - 1:
                    drone.delivered = True
                    continue

                previous_zone = drone.path[drone.path_index]
                next_zone = drone.path[drone.path_index + 1]
                key = tuple(sorted([previous_zone.name, next_zone.name]))
                connection = self.connection_map[key]
                
                if next_zone.zone_type == ZoneType.restricted:
                    if (connection.current_drones < connection.max_link_capacity
                        and next_zone.current_drones < next_zone.max_drones):
                        connection.current_drones += 1
                        next_zone.current_drones += 1
                        drone.in_transit = True
                        drone.transit_destination = next_zone
                        turn_movements += f"{drone.ID}-{connection.name} "
                        previous_zone.current_drones -= 1

            # REGULAR SCENARIO
                else:

                    # if the next zone has the capacity and the connection allows it
                    if (connection.current_drones < connection.max_link_capacity
                        and next_zone.current_drones < next_zone.max_drones):
                        connection.current_drones += 1
                        drone.position = next_zone.name
                        drone.path_index += 1
                        next_zone.current_drones += 1
                        previous_zone.current_drones -= 1
                        turn_movements += (f"{drone.ID}-{Colors.get_colors(next_zone.color)}{drone.position} {Colors.get_colors(Colors.reset)}")

                        if drone.position == self.end_hub.name:
                            drone.delivered = True
                        drone.moved_this_turn = True

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
            
        # ASSIGN A COST TO EACH zone
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
                    new_cost += 0.5

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
