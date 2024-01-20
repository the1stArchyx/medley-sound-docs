#!/bin/python

# This is a dirty hack to make 8-bit signed raw audio samples loadable
# into Medley Sound editor.

import argparse
import struct

HUNK_start = b"\x00\x00\x03\xe7\x00\x00\x00\x00\x00\x00\x03\xe9"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A dirty hack to make 8-bit signed raw audio loadable into Medley Sound editor.",
                                     epilog="Maximum data length supported by Medley Sound is 32 KiB.  Longer source data will be truncated.")
    parser.add_argument("filename", help="Source sample data.  Output file name will be appended with '.hunk'.")
    args = parser.parse_args()

    with open(args.filename, "rb") as f_in:
        src_bytes = f_in.read()

    src_len = len(src_bytes)

    if src_len > 32768:
        src_bytes = src_bytes[0:32768]
        src_len = 32768
        print("Warning: Source data length is over 32 KiB and was truncated.")
    else:
        remainder = src_len % 4
        if remainder:
            src_bytes += bytes(remainder)
            src_len = len(src_bytes)

    hunk_len = src_len // 4

    with open(args.filename + ".hunk", "wb") as f_out:
        f_out.write(HUNK_start)
        f_out.write(struct.pack(">i", hunk_len))
        f_out.write(src_bytes)
