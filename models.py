from pydantic import BaseModel, model_validator, ValidationError, Field


# ZONE (OR HUB) INSIDE THE GRAPH
# DRONES NAVIGATE THROUGH ZONES
class Zone(BaseModel):
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str | None = None
    max_drones: int = 1
    hub_type: str

    @model_validator(mode="after")
    def validate_zone(self):
        allowed = {"normal", "blocked", "restricted", "priority"}
        if self.zone_type not in allowed:
            raise ValueError(f"Invalid zone type: {self.zone_type}.")
        
        if self.max_drones < 0:
            raise ValueError(f"Invalid max_drones count: {self.max_drones}.")

        return self

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
        self.position = Zone


# ENTIRE GRAPH STRUCTURE
# IS COMPOSED BY ZONES AND CONNECTIONS
# WILL MANAGE THE WHOLE SIMULATION PROCESS
class Graph(BaseModel): 
    zones: dict[str, Zone] = Field(default_factory=dict)
    connections: list[Connection] = Field(default_factory=list)
    drone_count: int = Field(default_factory=int)
    drones: list = Field(default_factory=list, exclude=True)
    start_hub: Zone
    end_hub: Zone

    # CHECK FOR VALID NUMBER OF DRONES
    @model_validator(mode="after")
    def validate_graph(self):
        if self.drone_count <= 0:
            raise ValueError("Drone count cannot be less than or equal to 0.")
        return self

    # CREATE AND INITIALIZE ZONES IN START HUB POSITION
    def create_drones(self) -> None:

        for i in range(1, self.drone_count + 1):
            self.drones.append(Drone(f"D{i}"))

        starting_hub = self.start_hub

        for drone in self.drones:
            drone.position = starting_hub.name

    # GET NEIGHBORING ZONES FOR A SPECIFIC ZONE
    def get_neighbors(self, zone) -> list[Zone]:
        
        neighbors = []
        for connection in self.connections:
            if connection.zone1 == zone.name:
                neighbors.append(self.zones[connection.zone2])
            if connection.zone2 == zone.name:
                neighbors.append(self.zones[connection.zone1])
        return neighbors


    # SIMULATE DRONE ROUTE
    def simulate(self):

        self.create_drones()
        print(self.get_neighbors(self.zones["waypoint2"]))

    @staticmethod
    def calculate_movement_cost():
        pass


# PROBLEME = ACCEDER AU DICT SANS LA STRING VARIABLE
