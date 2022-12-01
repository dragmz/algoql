from argparse import ArgumentParser
from lib import algoql

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("query")

    args = parser.parse_args()

    for row in algoql.execute(args.query):
        print(row)