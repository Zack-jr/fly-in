from pydantic import BaseModel, model_validator

class Zone(BaseModel):
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str | None = None
    max_drones: int = 1
    # start/end
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
        pass


class Graph(BaseModel):
    zones: dict[str, Zone]
    connections: list[Connection]

    @model_validator(mode="after")
    def validate_graph(self):
        pass

    ## avoir des fonctions pour ajouter au graph les
    ## zones, drones et connections pour creer un vraie object utilisable
