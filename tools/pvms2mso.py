#!/bin/python

import argparse
import struct
import sys

class PVMS:
    """A class to load a PVMS project file into."""

    # Index 0 is "undefined" in Medley Sound, so we'll use it for
    # something later.  For now it's just a constant 0.
    instruments = [0] + [[]] * 255
    scores = [0] + [[]] * 255
    tracks = [0] + [[]] * 255
    waves = [0] + [[]] * 255

    def __init__(self, source_bytes):
        """Initialise class data from source file bytes."""
        pointer = 8
        while pointer < len(source_bytes):
            match source_bytes[pointer - 4:pointer]:
                case b"WAV2":
                    header_size = struct.unpack(">h", source_bytes[pointer:pointer + 2])[0]
                    if header_size != 0x1c:
                        print(f"Error: Specified wave header size ({header_size:02x}) is incorrect.")
                        sys.exit(-1)
                    pointer += 4
                    while True:
                        wave_index = struct.unpack(">h", source_bytes[pointer - 2:pointer])[0]
                        if wave_index < 0: # if sign bit is set, end of chunk reached.
                            pointer += 4
                            break
                        if wave_index < 1 or wave_index > 255:
                            print(f"Error: Wave index ({wave_index:04x}) out of bounds.")
                            sys.exit(-1)
                        self.waves[0] += 1
                        wave = [source_bytes[pointer:pointer + 16].decode(encoding="latin_1")] # 0 = ww_Name (str)
                        wave += [struct.unpack(">H", source_bytes[pointer + 20:pointer + 22])[0]] # 1 = ww_CycleSize (int)
                        wave += [source_bytes[pointer + 26]]                                   # 2 = ww_Octave
                        wave += [source_bytes[pointer + 25]]                                   # 3 = ww_FragFactor
                        wave += [source_bytes[pointer + 24]]                                   # 4 = ww_IsDoubleBufd
                        pointer += 0x1c
                        wave += [source_bytes[pointer:pointer + wave[1]]]                      # 5 = wave data
                        pointer += wave[1] + 2
                        self.waves[wave_index] = wave
                        
                case b"INS:":
                    header_size = struct.unpack(">h", source_bytes[pointer:pointer + 2])[0]
                    if header_size != 0x7a:
                        print(f"Error: Specified instrument header size ({header_size:02x}) is incorrect.")
                        sys.exit(-1)
                    pointer += 4
                    while True:
                        inst_index = struct.unpack(">h", source_bytes[pointer - 2:pointer])[0]
                        if inst_index < 0: # if sign bit is set, end of chunk reached.
                            pointer += 4
                            break
                        if inst_index < 1 or inst_index > 255:
                            print(f"Error: Track index ({inst_index:04x}) out of bounds.")
                            sys.exit(-1)
                        self.instruments[0] += 1
                        # Let's copy the instrument structure raw as
                        # it's the same in an MSOB.
                        self.instruments[inst_index] = source_bytes[pointer:pointer + 0x7a]
                        pointer += 0x7a + 2

                case b"TRK:":
                    header_size = struct.unpack(">h", source_bytes[pointer:pointer + 2])[0]
                    if header_size != 0x20:
                        print(f"Error: Specified track header size ({header_size:02x}) is incorrect.")
                        sys.exit(-1)
                    pointer += 4
                    while True:
                        track_index = struct.unpack(">h", source_bytes[pointer - 2:pointer])[0]
                        if track_index < 0: # if sign bit is set, end of chunk reached.
                            pointer += 4
                            break
                        if track_index < 1 or track_index > 255:
                            print(f"Error: Track index ({track_index:04x}) out of bounds.")
                            sys.exit(-1)
                        self.tracks[0] += 1
                        track = [source_bytes[pointer:pointer + 16].decode(encoding="latin_1")]
                        track_length = struct.unpack(">H", source_bytes[pointer + 20:pointer + 22])[0]
                        pointer += 0x22
                        track_data = b""
                        track_line = b""
                        i = 0
                        while track_line != b"\x80\x00":
                            track_line = source_bytes[pointer - 2:pointer]
                            pointer += 2
                            i += 2
                            # The logic below should be expanded to
                            # everything else skipped by the player
                            # routine to reduce redundant track data.
                            if track_line != b"\x00\x00":    # skip zero length rests
                                if track_line[0] != b"\x81": # skip TSIGN lines
                                    track_data += track_line
                        if i is not track_length:
                            print(f"Warning: track {track_index:02x} – actual track length {i:d} and header data {track_length:d} mismatch.")
                        track += [track_data]
                        self.tracks[track_index] = track
                        
                case b"SCO:":
                    header_size = struct.unpack(">h", source_bytes[pointer:pointer + 2])[0]
                    if header_size != 0x32:
                        print(f"Error: Specified score header size ({header_size:02x}) is incorrect.")
                        sys.exit(-1)
                    pointer += 4
                    while True:
                        score_index = struct.unpack(">h", source_bytes[pointer - 2:pointer])[0]
                        if score_index < 0: # if sign bit is set, end of chunk reached.
                            pointer += 4
                            break
                        if score_index < 1 or score_index > 255:
                            print(f"Error: Score index ({score_index:04x}) out of bounds.")
                            sys.exit(-1)
                        self.scores[0] += 1
                        # Let's copy the score structure raw as it's
                        # the same in an MSOB.
                        self.scores[score_index] = source_bytes[pointer:pointer + 0x7a]
                        pointer += 0x32 + 2

                case b"END.": # This shouldn't be needed as the
                              # pointer will run past the EOF but it's
                              # here just in case someone adds extra
                              # data after the end marker!
                    return
                case _:
                    print("Error: This PVMS source file is broken.")
                    sys.exit(-1)

    def export_instrument(instrument) -> bytes:
        """Export a single instrument for a Medley Sound Object."""
        pass

    def export_score(score) -> bytes:
        """Export a single score for a Medley Sound Object."""
        pass

    def export_track(track) -> bytes:
        """Export a single track for a Medley Sound Object."""
        pass

    def export_wave(wave) -> bytes:
        """Export a single wave for a Medley Sound Object."""
        pass


def askScores(source) -> tuple:
    pass


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
        pvms = PVMS(pvms_bytes)
        # 2. Start interactive mode to choose scores to export.
        scores = askScores(pvms)
        # 3. Create substitution tables to skip unused tracks, instruments, and waves.
        # 4. Export data.
        pass
    else:
        print("\nError: file type unknown.\n")


if __name__ == "__main__":
    main()

# EOF
