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


def huntMagic(inBuf: bytes) -> int:
    i = 0
    while (i < len(inBuf)):
        if inBuf[i] == 77:
            if inBuf[i:i+4] == b'MSOB':
                return i
        i += 1
    return -1

def createInsData(inBuf: bytes) -> bytes:
    outBuf = bytes.fromhex('49 4e 53 3a 00 7a') # 'INS:.z'

    pntr = getPointer(inBuf, 12)
    count = 255
    if getBoolean(inBuf, 37):
        count = inBuf[pntr-1]
    print(f'{count} instruments - table at {pntr:#010x}')

    if count > 1:
        for i in range(1, 1 + count):
            pntr += 4 # we're working sequentially, let's do it the old-fashioned way!
            data = getPointer(inBuf, pntr)
            if data == 0:
                print(f' -- Instrument {i:2x} is undefined.')
                continue
            if not getBoolean(inBuf, 36): # generate generic name if names are stripped
                insName += b'Instrument ' + bytes(f'{i:2x}', encoding='latin_1') + bytes(3)
            else:
                insName = inBuf[data:data+16]
                data += 16
            outBuf += bytes.fromhex(f'{i:04x}') # counter
            outBuf += insName
            outBuf += inBuf[data:data + 106] # copy instrument data
            print(f' -- Instrument {i:2x} : {insName.decode(encoding="latin_1")}')

    outBuf += bytes.fromhex('ff ff')
    return outBuf

def createScoData(inBuf: bytes) -> bytes:
    outBuf = bytes.fromhex('53 43 4f 3a 00 32') # 'SCO: 2'

    pntr = getPointer(inBuf, 4) # dig out the pointer to the table
    count = 255
    if getBoolean(inBuf, 37): # if we have partial tables
        count = inBuf[pntr-1] # there's a length in the byte before it
    print(f'{count} scores - table at {pntr:#010x}')

    if count > 1:
        for i in range(1, 1 + count):
            pntr += 4 # we're working sequentially, let's do it the old-fashioned way!
            data = getPointer(inBuf, pntr)
            if data == 0:
                print(f' -- Score {i} is undefined.')
                continue
            if not getBoolean(inBuf, 36): # generate name, if names are stripped
                scoName = b'Score ' + bytes(f'{i:2x}', encoding='latin_1') + bytes(8)
            else:
                scoName = inBuf[data:data+16]
                data += 16
            outBuf += bytes.fromhex(f'{i:04x}') # counter
            outBuf += scoName
            outBuf += inBuf[data:data + 34]
            print(f' -- Score {i:2x} : {scoName.decode(encoding="latin_1")}')
    
    outBuf += bytes.fromhex('ff ff')
    return outBuf

def createTrkData(inBuf: bytes) -> bytes:
    outBuf = bytes.fromhex('54 52 4b 3a 00 20') # 'TRK:. '

    pntr = getPointer(inBuf, 8)
    count = 255
    if getBoolean(inBuf, 37):
        count = inBuf[pntr-1]
    print(f'{count} tracks - table at {pntr:#010x}')

    if count > 1:
        for i in range(1, 1 + count):
            pntr += 4 # we're working sequentially, let's do it the old-fashioned way!
            data = getPointer(inBuf, pntr)
            if data == 0:
                print(f' -- Track {i} is undefined.')
                continue
            if not getBoolean(inBuf, 36): # generate name, if names are stripped
                trkName = b'Track ' + bytes(f'{i:2x}', encoding='latin_1') + bytes(8)
            else:
                trkName = inBuf[data:data+16]
                data += 16
            trkLen = 0
            while inBuf[data + trkLen:data + trkLen + 2] != b'\x80\x00':
                trkLen +=2
            trkLen += 2
            outBuf += bytes.fromhex(f'{i:04x}') # counter
            outBuf += trkName
            outBuf += bytes(4) + bytes.fromhex(f'{trkLen:04x}') + bytes(8) + b'\xff\xff'
            outBuf += inBuf[data:data + trkLen]
            print(f' -- Track {i:2x} : {int(trkLen/2):03} lines – {trkName.decode(encoding="latin_1")}')

    outBuf += bytes.fromhex('ff ff')
    return outBuf

def createWavData(inBuf: bytes) -> bytes:
    outBuf = bytes.fromhex('57 41 56 32 00 1c') # 'WAV2..'

    pntr = getPointer(inBuf, 16)
    count = 255
    if getBoolean(inBuf, 37):
        count = inBuf[pntr-1]
    print(f'{count} waves - table at {pntr:#010x}')

    if count > 0:
        for i in range(1, 1 + count):
            pntr += 4 # we're working sequentially, let's do it the old-fashioned way!
            data = getPointer(inBuf, pntr)
            if data == 0:
                print(f' -- Wave {i:2x} is undefined.')
                continue
            if not getBoolean(inBuf, 36): # generate generic name if names not in MSOB
                wavName += b'Wave ' + bytes(f'{i:2x}', encoding='latin_1') + bytes(9)
            else:
                wavName = inBuf[data:data+16]
                data += 16
            waveStart = data + 8
            waveLen = int(inBuf[data:data + 2].hex(), base=16)
            outBuf += bytes.fromhex(f'{i:04x}') # counter
            outBuf += wavName
            outBuf += bytes(4) # pointer to wave data, gets overwritten during load
            outBuf += inBuf[data:data + 4] # copy ww_CycleSize and ww_Dummy
            outBuf += inBuf[data + 6:data + 7] # ww_IsDoubleBufd
            outBuf += inBuf[data + 5:data + 6] # ww_FragFactor
            outBuf += inBuf[data + 4:data + 5] # ww_Octave
            outBuf += bytes(1)                 # ww_Pad
            outBuf += inBuf[waveStart:waveStart + waveLen] # copy wave data
            print(f' -- Wave {i:2x} : {waveLen:04x} - {wavName.decode(encoding="latin_1")}')

    outBuf += bytes.fromhex('ff ff')
    return outBuf


def createPVMS(inBuf: bytes) -> bytes:
    outBuf = bytes.fromhex('50 56 4d 53')    # magic bytes, 'PVMS'
    outBuf += createWavData(inBuf)
    outBuf += createInsData(inBuf)
    outBuf += createTrkData(inBuf)
    outBuf += createScoData(inBuf)
    outBuf += bytes.fromhex('45 4e 44 2e')   # terminator, 'END.'
    return outBuf


def main():
    print('MSOB-to-PVMS converter 0.1 by Archyx.\n')

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'rb') as f_in:
            in_bytes = f_in.read()

        # check magic bytes
        msoMagic = huntMagic(in_bytes)
        if msoMagic < 0:
            print('Error: Magic bytes not found!\n')
            sys.exit(1)
        if msoMagic > 0: # scrap everything before the magic bytes
            in_bytes = in_bytes[msoMagic:-1]
        
        out_bytes = createPVMS(in_bytes)
#        print(out_bytes)

        with open(sys.argv[1] + '.pvms', 'wb') as f_out:
            f_out.write(out_bytes)
    else:
        print('No filename given.')


if __name__ == "__main__":
    main()

# EOF
