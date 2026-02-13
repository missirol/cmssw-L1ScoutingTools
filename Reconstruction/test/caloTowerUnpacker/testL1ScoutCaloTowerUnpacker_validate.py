#!/usr/bin/env python3
import argparse
import os
import ROOT

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Validate the outputs of the "testL1ScoutCaloTowerUnpacker" workflow',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('--input1', type=str, default='tmp_testL1ScoutCaloTowers_out.root',
        help='Input file #1 (type: NanoAOD file with "L1DPG"-Nano flavour)')

    parser.add_argument('--input2', type=str, default='tmp_testL1ScoutCaloTowers_out2.root',
        help='Input file #2 (type: EDM file with L1Scouting data formats)')

    parser.add_argument('--output1', type=str, default=None,
        help='Output text file with the content of input file #1 (created only if the argument of --output1 is specified)')

    parser.add_argument('--output2', type=str, default=None,
        help='Output text file with the content of input file #2 (created only if the argument of --output2 is specified)')

    parser.add_argument('-v', '--verbosity', type=int, default=0,
        help='Level of verbosity in stdout (v <= 0: minimal, v == 1: moderate, v >= 2: high)')

    args = parser.parse_args()

    file1_root_filename = args.input1
    file1_print_filename = args.output1
    file2_root_filename = args.input2
    file2_print_filename = args.output2

    verbosity_lv1 = args.verbosity >= 1
    verbosity_lv2 = args.verbosity >= 2

    print(f'=== File-1: processing {file1_root_filename} ...')

    file1_print = None
    if file1_print_filename is not None:
        if os.path.exists(file1_print_filename):
            raise SystemExit(f'>>> Fatal Error - file already exists: {file1_print_filename}')
        file1_print = open(file1_print_filename, 'w')

    file1_calotower_strs = []
    file1 = ROOT.TFile.Open(file1_root_filename)
    tree1 = file1.Get("Events")
    nEvents1 = 0
    for event in tree1:
        nEvents1 += 1
        nCaloTowers1 = len(event.L1EmulCaloTower_iet)

        if file1_print is not None or verbosity_lv1:
            event_str = f'Event {nEvents1} ({nCaloTowers1} CaloTowers)'
            if file1_print is not None:
                file1_print.write(f'{event_str}\n')
            if verbosity_lv1:
                print(f'\n{event_str}')

        for idx in range(nCaloTowers1):
            hwEt = event.L1EmulCaloTower_iet[idx]
            hwEta = event.L1EmulCaloTower_ieta[idx]
            hwPhi = event.L1EmulCaloTower_iphi[idx]
            hwQual = event.L1EmulCaloTower_iqual[idx]
            hwEtRatio = event.L1EmulCaloTower_iratio[idx]
            file1_calotower_strs += [f'CaloTower: {hwEt}:{hwEta}:{hwPhi}:{hwQual}:{hwEtRatio}']

            if file1_print is not None or verbosity_lv2:
                if file1_print is not None:
                    file1_print.write(f'{file1_calotower_strs[-1]}\n')
                if verbosity_lv2:
                    print(f'{file1_calotower_strs[-1]}')

    if file1_print is not None:
        file1_print.close()

    file1_nCaloTowers = len(file1_calotower_strs)
    print(f'=== File-1: processed ({nEvents1} events, {file1_nCaloTowers} CaloTowers)\n')

    print(f'=== File-2: processing {file2_root_filename} ...')

    file2_print = None
    if file2_print_filename is not None:
        if os.path.exists(file2_print_filename):
            raise SystemExit(f'>>> Fatal Error - file already exists: {file2_print_filename}')
        file2_print = open(file2_print_filename, 'w')

    file2_calotower_strs = []
    file2 = ROOT.TFile.Open(file2_root_filename)
    tree2 = file2.Get("Events")
    file2_idx = 0
    nOrbits2, nBXs2 = 0, 0
    for event in tree2:
        nOrbits2 += 1
        bxs = event.l1ScoutingRun3CaloTowerOrbitCollection_l1sCaloTowers_CaloTower_SCPU.getFilledBxs()
        nBXs2 += len(bxs)
        for bx in bxs:
            nCaloTowers2 = event.l1ScoutingRun3CaloTowerOrbitCollection_l1sCaloTowers_CaloTower_SCPU.getBxSize(bx)

            if file2_print is not None or verbosity_lv1:
                event_str = f'  Orbit {nOrbits2}, BX {bx} ({nCaloTowers2} CaloTowers)'
                if file2_print is not None:
                    file2_print.write(f'{event_str}\n')
                if verbosity_lv2:
                    print(f'\n{event_str}')

            for idx in range(nCaloTowers2):
                obj = event.l1ScoutingRun3CaloTowerOrbitCollection_l1sCaloTowers_CaloTower_SCPU.getBxObject(bx, idx)
                hwEt = obj.hwEt()
                hwEta = obj.hwEta()
                hwPhi = obj.hwPhi()
                hwQual = obj.miscBits()
                hwEtRatio = obj.erBits()

                file1_idx = file2_idx % file1_nCaloTowers
                file2_calotower_strs += [f'CaloTower: {hwEt}:{hwEta}:{hwPhi}:{hwQual}:{hwEtRatio}']

                if file2_print is not None or verbosity_lv2:
                    if file2_print is not None:
                        file2_print.write(f'{file2_calotower_strs[-1]}\n')
                    if verbosity_lv2:
                        print(f'{file2_calotower_strs[-1]}')

                if file2_calotower_strs[-1] != file1_calotower_strs[file1_idx]:
                    err_msg = f'>>> Fatal Error: unexpected value in file-2 at index {file2_idx}\n\n'
                    err_msg += f'  File-1[{file1_idx}] = {file1_calotower_strs[file1_idx]}\n'
                    err_msg += f'  File-2[{file2_idx}] = {file2_calotower_strs[-1]}\n'
                    raise SystemExit(err_msg)

                file2_idx += 1

    if file2_print is not None:
        file2_print.close()

    print(f'=== File-2: processed ({nOrbits2} orbits, {nBXs2} BXs, {file2_idx} CaloTowers)\n')
    print(f'=== Test passed - same CaloTowers in File-1 and File-2 !')
