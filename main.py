import argparse

def main(args):
    print(args)
    print(args.file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="test_data/debug_10.txt", type=str, help="Test data to load.")

    main(parser.parse_args())