from models import Zone, Connection, Graph

class Parser():
    def __init__(self, filename):
        self.filename = filename
        self.drone_count = None
        self.start_hub = None
        self.graph = Graph()
        self.connections = []


    def parse(self):
        with open(self.filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                result = self.parse_line(line)
                if isinstance(result, int):
                    self.drone_count = result
                if isinstance(result, Zone):
                    self.graph.zones[result.name] = result
                elif isinstance(result, Connection):
                    self.graph.connections.append(result)
                
    @staticmethod
    def parse_line(line):
        if line.startswith("nb_drones"):
            return int(line.split(":")[1].strip())
        if line.startswith("start_hub") or line.startswith("end_hub") or line.startstwith("hub"):
            _prefix, rest  = line.split(":")
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
                meta[key] = value

            return Zone(name=name, x=x, y=y, color=meta.get("color", None), max_drones=meta.get("max_drones", 1))
        
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
            
            zone1, zone2 = main.strip().split("-")

            return Connection(zone1=zone1, zone2=zone2, max_link_capacity=capacity)

