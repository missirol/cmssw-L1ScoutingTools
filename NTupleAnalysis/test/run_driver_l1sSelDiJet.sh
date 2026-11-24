#!/bin/bash -e

TARGET_DIR=out2_l1sSelDiJet
[ $# -lt 1 ] || TARGET_DIR="${1}"

SELEC_TYPE=1
[ $# -lt 2 ] || SELEC_TYPE="${2}"

THIS_DIR=$(cd $(dirname -- "${BASH_SOURCE[0]}") && pwd)

INPUT_DIR=/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/missirol/l1scout/ntuples/261119

EXE_CMD="bdriver2 -s ${THIS_DIR}/run.py"
EXE_CMD+=" -p L1ScoutSelDiJetAnalysisDriver"
EXE_CMD+=" --os ${SCRAM_ARCH::3}"

${EXE_CMD} \
  -i "${INPUT_DIR}/L1ScoutingSelection_Run2026D/*/*.root" \
  -o "${TARGET_DIR}"/sel"${SELEC_TYPE}"/jobs/L1ScoutingSelection_Run2026D \
  --opt selectionType=${SELEC_TYPE} \
  --JobFlavour longlunch \
  -f 10

for signalInputFile in $(ls -1 "${INPUT_DIR}"/RSGravTo2Q_*.root); do
  signalLabel=$(basename "${signalInputFile}")
  signalLabel=${signalLabel::-5}

  for selecType in "${SELEC_TYPE}" 2; do

    ${EXE_CMD} \
      -i "${signalInputFile}" \
      -o "${TARGET_DIR}"/sel"${selecType}"/jobs/"${signalLabel}" \
      --opt selectionType=${selecType} \
      --JobFlavour espresso \
      -f 1
  done
done

SELEC_TYPE=2
${EXE_CMD} \
  -i "${INPUT_DIR}/L1Scouting_Run2026D/*/*.root" \
  -o "${TARGET_DIR}"/sel"${SELEC_TYPE}"/jobs/L1Scouting_Run2026D \
  --opt selectionType=${SELEC_TYPE} \
  --JobFlavour microcentury \
  -f 1
