#!/bin/python

import argparse

def main():
    parser = argparse.ArgumentParser(description="Optimising converter to convert Medley Sound projects to Medley Sound objects.",
                                     epilog="See https://github.com/the1stArchyx/medley-sound-docs for the latest iteration.")
    parser.add_argument("filename", help="Medley Sound project (the PVMS format Medley Sound Editor writes) file to convert")
    args = parser.parse_args()

    with open(args.filename, "rb") as f_in:
        pvms_bytes = f_in.read()

    # check magic bytes
    if pvms_bytes[0:4] == b"PVMS":
        # continue
        pass
    else:
        print("\nError: file type unknown.\n")


if __name__ == "__main__":
    main()

# EOF
