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


class Colors(Enum):
    red = "red"
    green = "green"
    blue = "blue"
    yellow = "yellow"
    cyan = "cyan"
    black = "black"
    magenta = "magenta"

    violet = "violet"
    gold = "gold"
    orange = "orange"
    purple = "purple"
    brown = "brown"
    lime = "lime"
    crimson = "crimson"
    maroon = "maroon"
    darkred = "darkred"

    rainbow = "rainbow"
    reset = "\033[0m"

    def get_colors(self):
        colors = {
            Colors.red: "\033[31m",
            Colors.green: "\033[32m",
            Colors.blue:  "\033[34m",
            Colors.yellow:  "\033[33m",
            Colors.cyan:  "\033[36m",
            Colors.black:  "\033[30m",
            Colors.magenta: "\033[35m",

            Colors.violet: "\033[38;5;93m",
            Colors.gold: "\033[38;5;220m",
            Colors.orange: "\033[38;5;208m",
            Colors.purple: "\033[38;5;129m",
            Colors.brown: "\033[38;5;94m",
            Colors.lime: "\033[38;5;118m",
            Colors.crimson: "\033[38;5;160m",
            Colors.maroon: "\033[38;5;52m",
            Colors.darkred: "\033[38;5;88m",
            Colors.reset: "\033[0m"
    }

        return colors[self]
    
    def rainbow_text(text: str) -> str:
        raimbow_colors = ["\033[31m", "\033[33m", "\033[32m", "\033[36m", "\033[34m", "\033[35m"]
        result = ""
        for i, char in enumerate(text):
            result += raimbow_colors[i % len(raimbow_colors)] + char

        return result + "\033[0m"


# ZONE (OR HUB) INSIDE THE GRAPH
# DRONES NAVIGATE THROUGH ZONES
class Zone(BaseModel):
    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.normal
    color: Colors | None
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