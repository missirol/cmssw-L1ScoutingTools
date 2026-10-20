#!/bin/bash -e

TARGET_DIR=out2_l1sSelDiJet
[ $# -lt 1 ] || TARGET_DIR="${1}"

SELEC_TYPE=0
[ $# -lt 2 ] || SELEC_TYPE="${2}"

batch_driver.py \
  -p L1ScoutSelDiJetAnalysisDriver \
  -i /eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/missirol/l1scout/ntuples/260910/L1ScoutingSelection_Run2026D/*.root \
     /eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/missirol/l1scout/ntuples/261005/ZprimeToQQ_M*_TuneCP5_13p6TeV_pythia8.root \
  -o "${TARGET_DIR}"_sel"${SELEC_TYPE}"/jobs \
  --JobFlavour espresso \
  --opt selectionType="${SELEC_TYPE}" \
  -n 1000000
