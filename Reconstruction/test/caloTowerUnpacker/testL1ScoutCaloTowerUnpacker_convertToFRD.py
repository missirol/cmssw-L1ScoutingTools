#!/usr/bin/env python3
"""
Script to convert a NanoAOD file including "L1Nano" branches
to FRD files for L1-Scouting with CaloTower-related information 

Original Author: Rocco Ardino (CERN)
"""
import argparse
import awkward
import json
import numpy
import os
import struct
import subprocess
import tempfile
import uproot

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument('-i', '--inputFile', type=str, default=None, required=True,
                    help='Path to NanoAOD input file')

parser.add_argument('-l', '--caloTowerLabel', type=str, default='L1EmulCaloTower',
                    help='Prefix of CaloTower-related branches in NanoAOD input file')

parser.add_argument('-n', '--numOrbits', type=int, default=10,
                    help='Number of orbits in the output file(s)')

args = parser.parse_args()

collBXs = None
try:
    fillingSchemeFile_url = 'https://gitlab.cern.ch/lhc-injection-scheme/injection-schemes/-/raw/7a04f57ecf1b6f97effa8f2433b68a0e767f9400/25ns_2352b_2340_2004_2133_108bpi_24inj.json'
    with tempfile.NamedTemporaryFile() as tmp:
        subprocess.run(f'wget {fillingSchemeFile_url} -O {tmp.name}'.split(), stdout = subprocess.DEVNULL, stderr = subprocess.STDOUT)
        fs = json.load(open(tmp.name))
        collBXs = (numpy.array(fs["collsIP1/5"])-1)//10 + 1
except Exception as ex:
    raise SystemExit(f'>>> Fatal Error: failed to obtain the list of colliding BCIDs from\n    {fillingSchemeFile_url}\n\n{ex}')

events = uproot.open(args.inputFile)["Events"].arrays()

L1CT = awkward.zip({
    "hwPt"     : events[f"{args.caloTowerLabel}_iet"],
    "hwEta"    : events[f"{args.caloTowerLabel}_ieta"],
    "hwPhi"    : events[f"{args.caloTowerLabel}_iphi"],
    "miscBits" : events[f"{args.caloTowerLabel}_iqual"],
    "ehrBits"  : events[f"{args.caloTowerLabel}_iratio"]
})

#L1CT = L1CT[numpy.abs(L1CT.hwEta * 0.087) < 2.5]
L1CT = awkward.values_astype(L1CT, numpy.int64)

def encode_ct(ct, enc=False):
    def c2(n, nb):
        if n < 0:
            c = (1 << nb) + n
            return c
        else:
            return n

    w32b  = 0
    w32b += (ct.hwPt         <<  0) & 0x000001ff
    w32b += (ct.ehrBits      <<  9) & 0x00000e00
    w32b += (ct.miscBits     << 12) & 0x0000f000
    w32b += (ct.hwPhi        << 16) & 0x00ff0000
    w32b += (c2(ct.hwEta, 8) << 24) & 0xff000000

    if enc:
        return struct.pack('I', w32b)
    else:
        return w32b

def decode_ct(word):
    ct = {
        "hwPt": word & 0x000001ff,
        "ehrBits": (word & 0x00000e00) >> 9,
        "miscBits": (word & 0x0000f000) >> 12,
        "hwPhi": (word & 0x00ff0000) >> 16,
        "hwEta": (word & 0xff000000) >> 24,
    }
    return ct

def encode_bx(bxnum, orbitnum, cts):
    rawdata  = struct.pack('I', len(cts))
    rawdata += struct.pack('I', bxnum)
    rawdata += struct.pack('I', orbitnum)

    for ct in cts:
        rawdata += encode_ct(ct, enc=True)

    return rawdata

def c2_ak(n, nb):
    return ((1 << nb) + n) * (n<0) + n*(n>0) 

def encode_ct_ak(ct, enc=False):
    w32b = ct.hwPt * 0
    w32b = w32b + ((ct.hwPt            <<  0) & 0x000001ff)
    w32b = w32b + ((ct.ehrBits         <<  9) & 0x00000e00)
    w32b = w32b + ((ct.miscBits        << 12) & 0x0000f000)
    w32b = w32b + ((ct.hwPhi           << 16) & 0x00ff0000)
    w32b = w32b + ((c2_ak(ct.hwEta, 8) << 24) & 0xff000000)

    return numpy.array(w32b, dtype='uint32').tobytes()

def encode_bx_ak(bxnum, orbitnum, cts):
    rawdata  = struct.pack('I', len(cts))
    rawdata += struct.pack('I', bxnum)
    rawdata += struct.pack('I', orbitnum)
    rawdata += encode_ct_ak(cts, enc=True)

    return rawdata

eh_version = 6
eh_flags = 0
eh_crc32c = 0

class frd_file_header_v2:
    ver_id = "RAW_0002".encode() # 64 (offset 0B)
    header_size = 32             # 16 (offset 8B)
    data_type = 20               # 16 (offset 10)
    event_count = 0              # 32 (offset 12B)
    run_number = 0               # 32 (offset 16B)
    lumisection = 0              # 32 (offset 20B)
    file_size = 0                # 64 (offset 24B)

# shortcut: take run number and LS number from the first event, and use zero as index
run = events["run"][0]
ls = events["luminosityBlock"][0]
index = 0
src_id = 32

num_orbits = max(0, args.numOrbits)
patience = 1

try:
    os.makedirs(f"run{run}")
except:
    pass

fout = open(f"run{run}/run{run}_ls{str(ls).zfill(4)}_index{str(index).zfill(6)}.raw", 'wb')

# write file header
fout.write(bytes(32))

# loop over orbits
izb = 0
fsize = 32
for i in range(1, num_orbits + 1):

    nbxs = 0
    orbitdata = bytes()
    for j in collBXs:
        # consider only 2 timeslices
        if (j%9 != 0 ) and (j%9 != 1):
            continue

        orbitdata += encode_bx_ak(j, i, L1CT[izb])
        izb += 1
        if izb == len(L1CT):
            izb = 0 # roll over

    if i%patience == 0:
        print(f"At orbit {i} (size = {len(orbitdata)/2**20:1.3f}MB)")

    eh_raw  = bytes()
    eh_raw += struct.pack('H', eh_version)
    eh_raw += struct.pack('H', eh_flags)
    eh_raw += struct.pack('I', run)
    eh_raw += struct.pack('I', ls)
    eh_raw += struct.pack('I', i)
    eh_raw += struct.pack('I', 4 + len(orbitdata))
    eh_raw += struct.pack('I', eh_crc32c)
    eh_raw += struct.pack('I', src_id)
    fout.write(eh_raw + orbitdata)
    fsize += len(eh_raw) + len(orbitdata)

# update file header
fh = frd_file_header_v2()
fh.event_count = num_orbits
fh.run_number = run
fh.lumisection = ls
fh.file_size = fout.tell()
fout.seek(0, 0)
fout.write(frd_file_header_v2.ver_id)
fout.write(struct.pack('H', fh.header_size))
fout.write(struct.pack('H', fh.data_type))
fout.write(struct.pack('I', fh.event_count))
fout.write(struct.pack('I', fh.run_number))
fout.write(struct.pack('I', fh.lumisection))
fout.write(struct.pack('Q', fh.file_size))
fout.close()
