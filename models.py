from pydantic import BaseModel, model_validator, ValidationError, Field
from collections import defaultdict
from typing import List
from enum import Enum
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

    # CREATE AND INITIALIZE ZONES IN START HUB POSITION
    def create_drones(self) -> None:

        for i in range(1, self.drone_count + 1):
            self.drones.append(Drone(f"D{i}"))

        for drone in self.drones:
            drone.position = self.start_hub.name
            drone.path = self.dijkstra(self.start_hub, self.end_hub)

    # GET NEIGHBORING ZONES FOR A SPECIFIC ZONE
    def get_neighbors(self, zone) -> list[Zone]:
        return self.adjacency[zone.name]

    def adjacency_maker(self) -> None:

        # automatically initializes keys
        adjacency_dict = defaultdict(list)

        # loop through the connections to create a dict of node: neighboring nodes
        for connection in self.connections:
            adjacency_dict[connection.zone1].append(self.zones[connection.zone2])
            adjacency_dict[connection.zone2].append(self.zones[connection.zone1])

        self.adjacency = adjacency_dict


    # SIMULATE DRONE ROUTE
    def simulate(self) -> None:

        turn_movements = ""
        self.create_drones()

        # while the drones are not all delivered
        while not all(drone.delivered for drone in self.drones):

            # for every drone
            for drone in self.drones:

                # if it's delivered -> skip
                if drone.delivered:
                    continue

                previous_zone = drone.path[drone.path_index]
                next_zone = drone.path[drone.path_index + 1]

                if next_zone.current_drones < next_zone.max_drones:
                    drone.position = next_zone.name
                    drone.path_index += 1
                    next_zone.current_drones += 1
                    previous_zone.current_drones -= 1
                    turn_movements += (f"{drone.ID}-{drone.position} ")

                    if drone.position == self.end_hub.name:
                        drone.delivered = True
                else:
                    continue

            print(turn_movements)
            turn_movements = ""

    
    # FINDS SHORTEST PATH FROM ENTRY TO EXIT
    def dijkstra(self, start : Zone, end: Zone) -> List[Zone]:

        distances = {}
        path = []
        heap = [(0, start.name)]
        came_from : dict[str, str] = {}


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


# 1. PATHFINDING
#   -implement dijkstra
#   -respect costs
#   output: one path start -> end

# 2. GENERATE MULTIPLE PATHS
#   -Run Djikstra multiple times
#   - slightly penalize used nodes/edges
#   - keep 2-4 different paths

# 3. ASSIGN DRONES
#   -Distribute drones across paths:
#       ex: drone.path = paths[i % len(path)]

# 4. DRONE STATE
#   - each drone needs an index, remaining turns

# 5. SIMULATION LOOP
#   for each turn, plan moves -> apply moves -> print output

# 6. MOVEMENT RULE (per drone)
#   - Move only if:
#       - zone has space
#       - connection has capacity
#   - else -> wait

# 7. CONSTRAINTS (must-have)
#   - zone capacity
#   - connection capacity

# 8. RESTRICTED ZONES
#   - movement takes two turns
#   - cannot stop mid-way

# 9. APPLY MOVES SAFELY
#   - don't move instantly 
#   - first: decide all moves
#   - then: apply all together

# 10. BASIC optimization
#   - Don't release all drones at once
#   - Send them gradually(avoid congestion)

# Paths -> Assign -> Simulate with constraints