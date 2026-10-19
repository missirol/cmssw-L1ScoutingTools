#!/bin/bash -e

TARGET_DIR=out2_l1sSelDiJet
[ $# -eq 0 ] || TARGET_DIR="${1}"

batch_driver.py \
  -p L1ScoutSelDiJetAnalysisDriver \
  -i /eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/missirol/l1scout/ntuples/260910/L1ScoutingSelection_Run2026D/*.root \
     /eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/missirol/l1scout/ntuples/261005/ZprimeToQQ_M*_TuneCP5_13p6TeV_pythia8.root \
  -o "${TARGET_DIR}"_sel"${SEL_TYPE}"/jobs \
  --JobFlavour espresso \
  --opt selectionType=1 \
  -n 1000000
