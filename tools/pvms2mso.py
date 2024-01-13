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
        # 1. Read PVMS into an object and sanity check it.
        # 2. Start interactive mode to choose scores to export.
        # 3. Create substitution tables to skip unused tracks, instruments, and waves.
        # 4. Export data, trim track lines not used by the player routine.
        pass
    else:
        print("\nError: file type unknown.\n")


if __name__ == "__main__":
    main()

# EOF
