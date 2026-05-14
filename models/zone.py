from pydantic import BaseModel, model_validator
from enum import Enum


# ASSIGN A COST TO EACH ZONE_TYPE
# PYDANTIC WILL CONVERT STR INTO ENUM
class ZoneType(Enum):
    normal = "normal"
    priority = "priority"
    restricted = "restricted"
    blocked = "blocked"

    def movement_cost(self) -> float:

        costs = {
            ZoneType.normal : 1,
            ZoneType.restricted : 2,
            ZoneType.blocked : float('inf'),
            ZoneType.priority : 1,
        }

        return costs[self]


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
        
        if isinstance(self.zone_type, str):
            self.zone_type = ZoneType[self.zone_type]
    
        return self

    def get_movement_cost(self):
        return self.zone_type.movement_cost()