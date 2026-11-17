#!/bin/bash -e

TARGET_DIR=out2_l1sSelDiJet
[ $# -lt 1 ] || TARGET_DIR="${1}"

SELEC_TYPE=0
[ $# -lt 2 ] || SELEC_TYPE="${2}"

THIS_DIR=$(cd $(dirname -- "${BASH_SOURCE[0]}") && pwd)

run_driver() {
  bdriver2 -s "${THIS_DIR}"/run.py \
    -p L1ScoutSelDiJetAnalysisDriver \
    --opt selectionType="${SELEC_TYPE}" \
    --os "${SCRAM_ARCH::3}" $@
}

run_driver \
  -i "/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/missirol/l1scout/ntuples/261104/L1ScoutingSelection_Run2026D/*/*.root" \
  -o "${TARGET_DIR}"_sel"${SELEC_TYPE}"/jobs/L1ScoutingSelection_Run2026D \
  --JobFlavour microcentury \
  -f 10

for mass in 200 300 400 500; do
  run_driver \
    -i /eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/missirol/l1scout/ntuples/261005/ZprimeToQQ_M"${mass}"_TuneCP5_13p6TeV_pythia8.root \
    -o "${TARGET_DIR}"_sel"${SELEC_TYPE}"/jobs/ZprimeToQQ_M"${mass}"_TuneCP5_13p6TeV_pythia8 \
    --JobFlavour espresso \
    -f 1
done

SELEC_TYPE=2
run_driver \
  -i "/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/missirol/l1scout/ntuples/261117/L1Scouting_Run2026D/*/*.root" \
  -o "${TARGET_DIR}"_sel"${SELEC_TYPE}"/jobs/L1Scouting_Run2026D \
  --JobFlavour microcentury \
  -f 1
