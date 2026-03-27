import argparse

def read_data_from_file(filepath):
    file = open(filepath, 'r')
    data = file.readlines()
    file.close()
    data = list(map(lambda x:x.split(' '), data))
    data = list(map(lambda x:[int(x[0]), int(x[1])], data))
    return {
        "n": data[0][0],
        "W": data[0][1],
        "list_price_weight": data[1:]
    }

def main(args):
    knapsack_data = read_data_from_file(args.file)
    print(knapsack_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="test_data/debug_10.txt", type=str, help="Test data to load.")

    main(parser.parse_args())