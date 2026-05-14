from typing import List
from models.zone import Zone

class Drone():
    def __init__(self, drone_id: str):
        self.ID = drone_id
        self.position = ""
        self.path : List[Zone] = []
        self.delivered : bool = False
        self.path_index : int = 0
        self.in_transit: bool = False
        self.transit_destination : Zone = None
        self.moved_this_turn : bool = False
