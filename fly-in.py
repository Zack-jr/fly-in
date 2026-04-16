from sys import argv
from parsing import Parser


def main():

    if len(argv) != 2 or not argv[1].endswith('.txt'):
        print("Usage: python3 fly-in.py input.txt.")
        return
    else:
        try:
            graph = Parser(argv[1]).parse()
            print(graph.drone_count)
        except ValueError as e:
            msg = e.errors()[0]["msg"]
            msg = msg.strip("Value error, ")
            print(f"Error during parsing: {msg}")
            return


if __name__ == '__main__':
    main()