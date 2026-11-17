#!/bin/bash -ex

[ $# -eq 1 ] || exit 1

run_test() {
  cmsDriver.py tmp \
    --nThreads 1 --nStreams 0 --nConcurrentLumis 1 \
    --geometry DB:Extended --mc \
    --no_exec -n 100 \
    --step RAW2DIGI,NANO:@GENLite+@L1ScoutCaloTowersMC \
    --datatier NANOAOD --eventcontent NANOAOD --process NANO \
    --customise_commands "process.NANOAODoutput.outputCommands += ['drop edmTriggerResults_*_*_*']" \
    --python_filename "${1}".py --filein "${2}" --fileout "${1}"_out.root --era "${3}" --conditions "${4}" "${@:5}"

  edmConfigDump "${1}".py > "${1}"_dump.py
  cmsRun "${1}"_dump.py &> "${1}"_dump.log
  rm -rf __pycache__
}

run_test test_era2024_gt2024 "${1}" Run3_2024 140X_mcRun3_2024_realistic_v26
run_test test_era2024_gt2025 "${1}" Run3_2024 151X_mcRun3_2025_realistic_v6
run_test test_era2024_gt2024_caloParams2025 "${1}" Run3_2024 140X_mcRun3_2024_realistic_v26 --custom_conditions L1TCaloParams_2025_v0_3_MC,L1TCaloParamsRcd
run_test test_era2025_gt2024 "${1}" Run3_2025 140X_mcRun3_2024_realistic_v26
