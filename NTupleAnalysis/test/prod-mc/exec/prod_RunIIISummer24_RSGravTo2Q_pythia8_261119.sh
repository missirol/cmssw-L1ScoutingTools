#!/bin/bash -ex

[ $# -eq 2 ] || exit 1

OUT_DIR="${1}"
OUT_DIR_CMSRUN="${2}"

THIS_DIR=$(cd $(dirname -- "${BASH_SOURCE[0]}") && pwd)

# Create grid-certificate proxy (if not already in place)
if [ ! -f "${X509_USER_PROXY}" ]; then
  voms-proxy-init --voms cms --rfc --valid 168:00
fi

SAMPLE_LABELS=(
  RSGravTo2Q_kMpl01_M_200_TuneCP5_13p6TeV_pythia8
  RSGravTo2Q_kMpl01_M_225_TuneCP5_13p6TeV_pythia8
  RSGravTo2Q_kMpl01_M_250_TuneCP5_13p6TeV_pythia8
  RSGravTo2Q_kMpl01_M_300_TuneCP5_13p6TeV_pythia8
  RSGravTo2Q_kMpl01_M_350_TuneCP5_13p6TeV_pythia8
  RSGravTo2Q_kMpl01_M_400_TuneCP5_13p6TeV_pythia8
  RSGravTo2Q_kMpl01_M_450_TuneCP5_13p6TeV_pythia8
  RSGravTo2Q_kMpl01_M_500_TuneCP5_13p6TeV_pythia8
)

# Create list of EDM files for pileup sample
PILEUP_FILELIST="${THIS_DIR}"/../data/Neutrino_E10_gun_RunIIISummer24_PREMIX.txt
if [ ! -f "${PILEUP_FILELIST}" ]; then
  dasFilelist \
    -d /Neutrino_E-10_gun/RunIIISummer24PrePremix-Premixlib2024_140X_mcRun3_2024_realistic_v26-v1/PREMIX \
    -s T2_CH_CERN \
    -o "${PILEUP_FILELIST}" \
    --fail-if-empty \
    -j 8
fi

NUMTHREADS=4
JOBFLAVOUR=workday

for SAMPLE_LABEL in "${SAMPLE_LABELS[@]}"; do

  bdriverStepChain \
   -w "${THIS_DIR}"/../wfs/wf_RSGravTo2Q_TuneCP5_13p6TeV_pythia8.json \
   -f "${THIS_DIR}"/../fragments/"${SAMPLE_LABEL}"-fragment.py \
   -p filelist:"${PILEUP_FILELIST}" \
   -o "${OUT_DIR}"/"${SAMPLE_LABEL}" \
   -d "${OUT_DIR}"/"${SAMPLE_LABEL}"/cmssw_areas \
   --output-dir-cmsRun "${OUT_DIR_CMSRUN}"/"${SAMPLE_LABEL}" \
   --os "${SCRAM_ARCH::3}" --JobFlavour "${JOBFLAVOUR}" --cpus "${NUMTHREADS}" \
   -l 1 -j 1000 -n 1000
done
