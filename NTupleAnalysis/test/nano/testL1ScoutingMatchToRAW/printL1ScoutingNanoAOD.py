#!/usr/bin/env python3
import sys
import uproot

print(f'Opening file ({sys.argv[1]}) ...')
ufile = uproot.open(sys.argv[1])

print('Opening Tree ("Events") ...')
tree = ufile["Events"]

print('Getting luminosityBlock array...')
luminosityBlock_arr = tree["luminosityBlock"].array()

print('Getting orbitNumber array...')
orbitNumber_arr = tree["orbitNumber"].array()

print('Printing info...')
for idx, orbitNumber in enumerate(orbitNumber_arr):
    luminosityBlock = luminosityBlock_arr[idx]
    print(f'{luminosityBlock}:{orbitNumber}')
