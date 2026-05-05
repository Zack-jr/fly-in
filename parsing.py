from models import Zone, Connection, Graph

class Parser():
    # READS THE .TXT FILES
    # THIS CLASS'S GOAL IS TO RETURN A VALID GRAPH

    def __init__(self, filename):
        self.filename = filename

    # READ FROM THE FILE AND CREATE A GRAPH WITH CORRESPONDING ATTRIBUTES
    def parse(self):
        with open(self.filename, 'r') as f:
            connections = []
            zones = {}
            drone_count = 0

            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                result = self.parse_line(line)
                if isinstance(result, int):
                    drone_count = result
    
                if isinstance(result, Zone):
                    zones[result.name] = result
                    if result.hub_type == "start_hub":
                        start_hub = result
                    if result.hub_type == "end_hub":
                        end_hub = result
    
                elif isinstance(result, Connection):
                    connections.append(result)

            graph = Graph(zones=zones, connections=connections, drone_count=drone_count, start_hub=start_hub, end_hub=end_hub)

        return graph


    # PARSE A GIVEN LINE AND RETURNS A ZONE OR A CONNECTION
    @staticmethod
    def parse_line(line):
        meta_dict = {}
        if line.startswith("nb_drones"):
            return int(line.split(":")[1].strip())
        if line.startswith("start_hub") or line.startswith("end_hub") or line.startswith("hub"):
            prefix, rest  = line.split(":")
            if "[" in rest:
                main, meta = rest.split("[")
                meta = meta.strip("]")
            else:
                main = rest
                _meta_str = ""
            parts = main.split()
            name = parts[0]
            x = int(parts[1])
            y = int(parts[2])

            for item in meta.split():
                key, value = item.split("=")
                meta_dict[key] = value

            return Zone(hub_type=prefix, name=name, x=x, y=y, color=meta_dict.get("color", None), max_drones=meta_dict.get("max_drones", 1))

        if line.startswith("connection"):
            _, rest = line.split(":", 1)
            rest = rest.strip()

            if "[" in rest:
                main, meta_str = rest.split("[")
                meta_str = meta_str.strip("]")
                capacity = int(meta_str.split("=")[1])

            else:
                main = rest
                capacity = 1

                try:
                    zone1, zone2 = main.strip().split("-")
                except Exception:
                    raise ValueError("connection name cannot contain '-' characters")

            return Connection(zone1=zone1, zone2=zone2, max_link_capacity=capacity)

