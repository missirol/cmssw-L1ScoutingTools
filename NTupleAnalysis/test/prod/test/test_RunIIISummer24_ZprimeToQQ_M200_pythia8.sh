#!/bin/bash -ex

OUT_DIR="${CMSSW_BASE}"/../tmp_out
[ $# -eq 0 ] || OUT_DIR="${1}"

if [ -d "${OUT_DIR}" ]; then
  printf "%s\n" ">> ERROR -- target output directory already exists: ${OUT_DIR}"
  exit 1
fi

THIS_DIR=$(cd $(dirname -- "${BASH_SOURCE[0]}") && pwd)

# Create grid-certificate proxy (if not already in place)
if [ ! -f "${X509_USER_PROXY}" ]; then
  voms-proxy-init --voms cms --rfc --valid 168:00
fi

# Create list of EDM files for pileup sample
PILEUP_FILELIST="${THIS_DIR}"/../data/Neutrino_E10_gun_RunIIISummer24_PREMIX.txt
[ -f "${PILEUP_FILELIST}" ] || "${THIS_DIR}"/../data/create_files.sh

bdriverStepChain \
 -w "${THIS_DIR}"/../wfs/wf_ZprimeToQQ_TuneCP5_13p6TeV_pythia8.json \
 -f "${THIS_DIR}"/../fragments/fragment_ZprimeToQQ_M200_TuneCP5_13p6TeV_pythia8.py \
 -p filelist:"${PILEUP_FILELIST}" \
 -o "${OUT_DIR}" \
 -d "${OUT_DIR}"/cmssw_areas \
 --output-dir-cmsRun "${OUT_DIR}"/outputs \
 --os "${SCRAM_ARCH::3}" --JobFlavour longlunch --cpus 4 \
 -l 1 -j 1 -n 100
