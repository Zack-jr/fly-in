from pydantic import BaseModel, model_validator, ValidationError, Field

class Zone(BaseModel):
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str | None = None
    max_drones: int = 1

    @model_validator(mode="after")
    def validate_zone(self):
        allowed = {"normal", "blocked", "restricted", "priority"}
        if self.zone_type not in allowed:
            raise ValueError(f"Invalid zone type: {self.zone_type}.")
        
        if self.max_drones < 0:
            raise ValueError(f"Invalid max_drones count: {self.max_drones}.")

        return self


class Connection(BaseModel):
    zone1: str
    zone2: str
    max_link_capacity: int = 1

    @model_validator(mode="after")
    def validate_connection(self):
        if self.max_link_capacity < 0:
            raise ValueError("max_link_capacity cannot be negative")

        return self

class Drone():
    def __init__(self, drone_id: str):
        self.ID = drone_id
        self.position = None

class Graph(BaseModel):
    zones: list[Zone] = Field(default_factory=list)
    connections: list[Connection] = Field(default_factory=list)
    drone_count: int = Field(default_factory=int)
    drones: list = Field(default_factory=list, exclude=True)

    #check si le graph possede le bon nombre de connections/zones?
    @model_validator(mode="after")
    def validate_graph(self):
        if self.drone_count <= 0:
            raise ValueError("Drone count cannot be less than or equal to 0.")
        return self

    def create_drones(self) -> None:

        for i in range(1, self.drone_count + 1):
            self.drones.append(Drone(f"D{i}"))

    def simulate(self):
        self.create_drones()

        for drone in self.drones:
            drone.position = zones.

    @staticmethod
    def calculate_movement_cost():
        pass


    ## avoir des fonctions pour ajouter au graph les
    ## zones, drones et connections pour creer un vraie object utilisable
