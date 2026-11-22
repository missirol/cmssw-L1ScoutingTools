#!/bin/bash

datasets=(
  # MC (Winter25)
  /QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/Run3Winter25Digi-EpsilonPU_142X_mcRun3_2025_realistic_v9-v4/GEN-SIM-RAW
  /QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/Run3Winter25Digi-FlatPU0to120_142X_mcRun3_2025_realistic_v9-v4/GEN-SIM-RAW
  /TT_TuneCP5_13p6TeV_powheg-pythia8/Run3Winter25Digi-142X_mcRun3_2025_realistic_v7-v2/GEN-SIM-RAW

  # Data (Run2026D)
  /HLTPhysics/Run2026D-v1/RAW
  /L1Scouting/Run2026D-v1/L1SCOUT
  /L1ScoutingSelection/Run2026D-v1/L1SCOUT
)

for dataset in "${datasets[@]}"; do

  rucio add-rule \
    cms:"${dataset}" \
    1 \
    'rse_type=DISK&cms_type=real\tier=3\tier=0' \
    --grouping 'ALL' \
    --lifetime 13000000 \
    --ask-approval \
    --activity "User AutoApprove" \
    --comment "L1-Scouting 2026 performance studies"
done
unset dataset
