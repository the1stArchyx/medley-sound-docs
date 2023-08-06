#!/bin/python

import sys


def getBoolean(inBuf: bytes, offset: int) -> bool:
    if inBuf[offset] == 0:
        return False
    return True


def getPointer(inBuf: bytes, offset: int) -> int:
    # calculate an absolute pointer from a relative vector.
    vector = int(inBuf[offset:offset+4].hex(), base=16)
    if vector != 0:
        return vector + offset
    return 0


def getTable(inBuf: bytes, offset: int, partial: bool) -> list:
    count = 255
    if partial:
        count = inBuf[offset - 1]
        if count == 0:
            return [0]
    tbl = [count]
    for i in range(1, count + 1):
        tbl.append(getPointer(inBuf, 4 * i + offset))
    return tbl


def huntMagic(inBuf: bytes, inBufLen: int) -> int:
    i = 0
    while (i < inBufLen):
        if inBuf[i] == 77:
            if inBuf[i:i+4] == b'MSOB':
                return i
        i += 1
    return -1


def decode_msob(inBuf: bytes, inBufLen: int):
    # The pointer to magic bytes is the root for everything else and
    # may not always be at the beginning of the file!
    msoHeader = dict()
    msoHeader['base'] = huntMagic(inBuf, inBufLen)
    if msoHeader['base'] < 0:
        print('Magic bytes "MSOB" not found!\n')
        sys.exit()
    print('Magic bytes "MSOB" found at: ' + f"{msoHeader['base']:#010x}")
    if msoHeader['base'] > 0:
        print('All following offsets are relative to the location of magic bytes!')
        inBuf = inBuf[msoHeader['base']:-1]   # ...and we can scrap the object header as we have no need for it.

    msoHeader['scoTable'] = getPointer(inBuf, 4)
    msoHeader['trkTable'] = getPointer(inBuf, 8)
    msoHeader['insTable'] = getPointer(inBuf, 12)
    msoHeader['wavTable'] = getPointer(inBuf, 16)

    print('Score/Track/Instrument/Wave tables at: ' + f"{msoHeader['scoTable']:#010x}" + ' / ' + f"{msoHeader['trkTable']:#010x}" + ' / ' + f"{msoHeader['insTable']:#010x}" + ' / ' + f"{msoHeader['wavTable']:#010x}")

    # There's four reserved 4-byte vectors that are expected to be zero.
    for i in [20, 24, 28, 32]:
        j = int(inBuf[i:i+4].hex(), base=16)
        if j != 0:
            print('Unexpected value of a reserved field at ' + f"{i:#010x}" + ': ' + f"{j:#010x}")

    msoHeader['names'] = getBoolean(inBuf, 36)
    msoHeader['partTables'] = getBoolean(inBuf, 37)
    print('Flags:\n - Names are included: ' + str(msoHeader['names']) + '\n - Partial tables used: ' + str(msoHeader['partTables']))

    msoScoTable = [] + getTable(inBuf, msoHeader['scoTable'], msoHeader['partTables'])
    msoTrkTable = [] + getTable(inBuf, msoHeader['trkTable'], msoHeader['partTables'])
    msoInsTable = [] + getTable(inBuf, msoHeader['insTable'], msoHeader['partTables'])
    msoWavTable = [] + getTable(inBuf, msoHeader['wavTable'], msoHeader['partTables'])

    if msoHeader['names']:
        print('\nScore list:')
        i = 1
        while i <= msoScoTable[0]:
            if msoScoTable[i] != 0:
                p = msoScoTable[i]
                print(f" - {i:#04x}: {inBuf[p:p + 16].decode()}")
            i += 1

        print('\nTrack list:')
        i = 1
        while i <= msoTrkTable[0]:
            if msoTrkTable[i] != 0:
                p = msoTrkTable[i]
                print(f" - {i:#04x}: {inBuf[p:p + 16].decode()}")
            i += 1

        print('\nInstrument list:')
        i = 1
        while i <= msoInsTable[0]:
            if msoInsTable[i] != 0:
                p = msoInsTable[i]
                print(f" - {i:#04x}: {inBuf[p:p + 16].decode()}")
            i += 1

        print('\nWave list:')
        i = 1
        while i <= msoWavTable[0]:
            if msoWavTable[i] != 0:
                p = msoWavTable[i]
                for j in range(16):
                    if inBuf[p + j] == 0:
                        break
                name = inBuf[p:p + j].decode(encoding="latin_1")
                print(f" - {i:#04x}: {name:<16} // CycleSize = {inBuf[p + 16:p + 18].hex()} ; Octave = {inBuf[p + 20:p + 21].hex()} ; FragFactor = {inBuf[p + 21:p + 22].hex()} ; IsDoubleBufd = {inBuf[p + 22:p + 23].hex()}")
            i += 1

def main():
    print('MSOB decoder 0.1 by Archyx.\n')

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'rb') as f_in:
            in_bytes = f_in.read()
            in_bytecount = len(in_bytes)

        decode_msob(in_bytes, in_bytecount)
    else:
        print('No filename given.')


if __name__ == "__main__":
    main()

# EOF
