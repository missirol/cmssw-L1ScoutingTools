#!/usr/bin/env python3
import argparse
import os
import ROOT

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description = 'Create JSON files to reprocess L1-Scouting CaloL1 data of 2026',
        formatter_class = argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('--files-raw', nargs='+', required=True,
        help='Path to file in flat-NanoAOD format from standard "RAW" data set')

    parser.add_argument('--files-l1s', nargs='+', required=True,
        help='Path to file in flat-NanoAOD format from L1-Scouting data set')

    parser.add_argument('-n', '--maxEvents', type=int, default=-1,
        help='Maximum number of events to be processed, used only if greater than zero')

    parser.add_argument('--orbit-shift', type=int, default=0,
        help='Shift to apply to the orbit value of CaloTowers in L1-Scouting events, if --fix-l1s-data is specified')

    parser.add_argument('--bx-shift', type=int, default=0,
        help='Shift to apply to the BX value of CaloTowers in L1-Scouting events, if --fix-l1s-data is specified')

    parser.add_argument('--use-emulated-calotowers', action='store_true', default=False,
        help='For the events in file-raw, use emulated CaloTowers instead of unpacked ones')

    parser.add_argument('--fix-l1s-data', action='store_true', default=False,
        help='Modify values in L1-Scouting events')

    parser.add_argument('-v', '--verbose', action='store_true', default=False,
        help='Verbose output to stdout')

    args = parser.parse_args()

    maxEvents = args.maxEvents
    l1sExtraShift_orbitNumber = args.orbit_shift
    l1sExtraShift_bunchCrossing = args.bx_shift
    fatEvents = bool(not args.use_emulated_calotowers)
    fixL1ScoutingCaloTowers = args.fix_l1s_data

    print('-'*50)
    print(f'l1sExtraShift_orbitNumber = {l1sExtraShift_orbitNumber}')
    print(f'l1sExtraShift_bunchCrossing = {l1sExtraShift_bunchCrossing}')
    print('-'*50)

    print('Reading (run,ls,orbit,bx) values from standard file..')

    rawCaloTowerLabel = 'L1UnpackedCaloTower' if fatEvents else 'L1EmulCaloTower'

    link_map = {
      24: 35,
      25: 32,
      26: 34,
      27: 33,
      28: 30,
      29: 31,
      30: 28,
      31: 29,
      32: 25,
      33: 27,
      34: 26,
      35: 24,
    }

    bx0s_mod = set()
    for f0_path in args.files_raw:
        f0 = ROOT.TFile.Open(f0_path)
        t0 = f0.Get('Events')
        if args.verbose:
            print(f'  {f0_path}')
        for e0 in t0:
            if fatEvents and e0.nL1UnpackedCaloTower <= 0:
                continue
            bx0s_mod.add((e0.run, e0.luminosityBlock, e0.orbitNumber + l1sExtraShift_orbitNumber, e0.bunchCrossing + l1sExtraShift_bunchCrossing))

    print('Looking for (run,ls,orbit,bx) matches in L1-Scouting data..')

    matchCounter = 0

    bx0s = set()
    for f1_path in args.files_l1s:
        f1 = ROOT.TFile.Open(f1_path)
        t1 = f1.Get('Events')
        if args.verbose:
            print(f'  {f1_path}')
        for e1 in t1:
            if e1.nL1CaloTower <= 0:
                continue
            bx1 = (e1.run, e1.luminosityBlock, e1.orbitNumber, e1.bunchCrossing)

            if bx1 in bx0s_mod:
                matchCounter += 1

                ct1s = []
                for ct1_idx in range(e1.nL1CaloTower):
                    ct1s += [[
                        e1.L1CaloTower_hwEt[ct1_idx],
                        e1.L1CaloTower_erBits[ct1_idx],
                        e1.L1CaloTower_miscBits[ct1_idx],
                        e1.L1CaloTower_hwPhi[ct1_idx],
                        e1.L1CaloTower_hwEta[ct1_idx],
                    ]]
                ct1s.sort()

                if fixL1ScoutingCaloTowers:
                    # First MP7 firmware update to fix CaloTower-eta/phi values, see
                    # https://gitlab.cern.ch/scouting-demonstrator/calol2/-/merge_requests/13
                    afterFwFix = e1.run >= 403259

                    # Events from MP71 require an additional fix for the CaloTower-phi values
                    bx1_shifted = bx1[3] - l1sExtraShift_bunchCrossing
                    bx1_shifted = bx1_shifted if bx1_shifted > 0 else bx1_shifted + 3564
                    isFromMP71 = bx1_shifted % 9 == 8

                    ct1s_mod = []
                    for ct1 in ct1s:
                        old_hwPhi = ct1[3]
                        old_hwEta = ct1[4]

                        if afterFwFix:
                            isFirstWord = (old_hwPhi % 2) != 0
                            if old_hwEta < 0:
                                old_link = (old_hwPhi - 1) if (old_hwPhi % 2) == 0 else old_hwPhi
                            else:
                                old_link = (old_hwPhi - 2) if (old_hwPhi % 2) == 0 else (old_hwPhi - 1)
                        else:
                            isFirstWord = old_hwEta > 0
                            old_link = old_hwPhi - 1

                        new_link = link_map[old_link] if (isFromMP71 and old_link in link_map) else old_link

                        new_hwEta = abs(old_hwEta)
                        if (new_link % 2) != 0:
                            new_hwEta *= -1

                        link_phi = (new_link - 1) if (new_link % 2) != 0 else new_link
                        new_hwPhi = (link_phi + 1) if isFirstWord else (link_phi + 2)

                        ct1s_mod += [[
                            ct1[0],
                            ct1[1],
                            ct1[2],
                            new_hwPhi,
                            new_hwEta,
                        ]]
                    ct1s_mod.sort()
                    ct1s = ct1s_mod[:]

                outf_name = f'out_run{bx1[0]}_ls{bx1[1]}_orbit{bx1[2]-l1sExtraShift_orbitNumber}_bx{bx1[3]-l1sExtraShift_bunchCrossing}_l1s.txt'
                print(f'    {outf_name}')
                with open(outf_name, 'w') as outf:
                    outf.write(f'L1-Scouting data (run = {bx1[0]}, LS = {bx1[1]}, orbitNumber = {bx1[2]}, bunchCrossing = {bx1[3]})\n')
                    outf.write(f'CaloTowers Label = "L1CaloTower"\n')
                    outf.write(f'Number of CaloTowers = {len(ct1s)}\n')
                    outf.write(50*'-'+'\n')
                    outf.write('hwEt hwEta hwPhi erBits miscBits\n')
                    outf.write(50*'-'+'\n')
                    for ct1 in ct1s:
                        outf.write(f'{ct1[0]:>5d} {ct1[4]:>5d} {ct1[3]:>5d} {ct1[1]:>5d} {ct1[2]:>5d}\n')
                    outf.write(50*'-'+'\n')

                bx0s.add((bx1[0], bx1[1], bx1[2] - l1sExtraShift_orbitNumber, bx1[3] - l1sExtraShift_bunchCrossing))

                if maxEvents > 0 and matchCounter == maxEvents:
                    break

    print(f'Found {matchCounter} (run,ls,orbit,bx) matches in L1-Scouting data')

    print('Printing content of CaloTowers in standard data for (run,ls,orbit,bx) matches..')

    filesWithDiffs = []
    for f0_path in args.files_raw:
        f0 = ROOT.TFile.Open(f0_path)
        t0 = f0.Get('Events')
        for e0 in t0:
            bx0 = (e0.run, e0.luminosityBlock, e0.orbitNumber, e0.bunchCrossing)

            if bx0 in bx0s:
                ct0s = []
                for ct0_idx in range(getattr(e0, f'n{rawCaloTowerLabel}')):
                    ct0_hwEta = getattr(e0, f'{rawCaloTowerLabel}_ieta')[ct0_idx]
                    if abs(ct0_hwEta) > 29:
                        continue
                    ct0s += [[
                        getattr(e0, f'{rawCaloTowerLabel}_iet')[ct0_idx],
                        getattr(e0, f'{rawCaloTowerLabel}_iratio')[ct0_idx],
                        getattr(e0, f'{rawCaloTowerLabel}_iqual')[ct0_idx],
                        getattr(e0, f'{rawCaloTowerLabel}_iphi')[ct0_idx],
                        ct0_hwEta,
                    ]]
                ct0s.sort()

                outf_name = f'out_run{bx0[0]}_ls{bx0[1]}_orbit{bx0[2]}_bx{bx0[3]}_raw.txt'
                print(f'    {outf_name}')
                with open(outf_name, 'w') as outf:
                    outf.write(f'RAW data (run = {bx0[0]}, LS = {bx0[1]}, orbitNumber = {bx0[2]}, bunchCrossing = {bx0[3]})\n')
                    outf.write(f'CaloTowers Label = "{rawCaloTowerLabel}"\n')
                    outf.write(f'Number of CaloTowers = {len(ct0s)}\n')
                    outf.write(50*'-'+'\n')
                    outf.write('hwEt hwEta hwPhi erBits miscBits\n')
                    outf.write(50*'-'+'\n')
                    for ct0 in ct0s:
                        outf.write(f'{ct0[0]:>5d} {ct0[4]:>5d} {ct0[3]:>5d} {ct0[1]:>5d} {ct0[2]:>5d}\n')
                    outf.write(50*'-'+'\n')

                with open(outf_name, 'r') as txtf:
                    raw_lines = list(map(str.rstrip, txtf))
                with open(outf_name[:-8]+'_l1s.txt', 'r') as txtf:
                    l1s_lines = list(map(str.rstrip, txtf))

                if raw_lines[2:] != l1s_lines[2:]:
                    filesWithDiffs += [outf_name[:-8]+'_*.txt']

    print('-'*50)
    print(f'Number of events with mismatches: {len(filesWithDiffs)}')
    print('-'*50)

    for fileWithDiffs in filesWithDiffs:
        print(fileWithDiffs)
