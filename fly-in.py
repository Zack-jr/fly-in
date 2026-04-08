from sys import argv
from parsing import Parser


def main():

    if len(argv) != 3 or not argv[2].endswith('.txt'):
        print("Usage: python3 fly-in.py input.txt.")
        return
    else:
        parser = Parser(argv[2])





if __name__ == '__main__':
    main()