from pydantic import BaseModel, model_validator

class Connection(BaseModel):
    zone1: str
    zone2: str
    max_link_capacity: int = 1
    current_drones: int = 0
    name : str = ""

    @model_validator(mode="after")
    def validate_connection(self):
        if self.max_link_capacity < 0:
            raise ValueError("max_link_capacity cannot be negative")

        self.name = '-'.join(sorted([self.zone1, self.zone2]))

        return self