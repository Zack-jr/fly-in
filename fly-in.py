from sys import argv
from parsing import Parser
from models import ValidationError


def main():

    if len(argv) != 2 or not argv[1].endswith('.txt'):
        print("Usage: python3 fly-in.py input.txt.")
        return

    else:
        try:
            graph = Parser(argv[1]).parse()
            graph.simulate()
            for drone in graph.drones:
                print(drone.ID)

        except (ValueError, ValidationError) as e:

            if isinstance(e, ValidationError):
                msg = e.errors()[0]['msg'].strip("Value error, ")
                print(f"Error during parsing: {msg}")
                return
            else:
                print(f"Error during parsing: {e}")
                return
            

if __name__ == '__main__':
    main()