#!/bin/bash -ex

[ $# -eq 2 ] || exit 1

OUT_DIR="${1}"

if [ -d "${OUT_DIR}" ]; then
  printf "%s\n" ">> ERROR -- target output directory already exists: ${OUT_DIR}"
  exit 1
fi

OUT_DIR_CMSRUN="${2}"

if [ -d "${OUT_DIR_CMSRUN}" ]; then
  printf "%s\n" ">> ERROR -- target directory for cmsRun outputs already exists: ${OUT_DIR_CMSRUN}"
  exit 1
fi

THIS_DIR=$(cd $(dirname -- "${BASH_SOURCE[0]}") && pwd)

# Create grid-certificate proxy (if not already in place)
if [ ! -f "${X509_USER_PROXY}" ]; then
  voms-proxy-init --voms cms --rfc --valid 168:00
fi

SAMPLE_LABELS=(
  ZprimeToQQ_M200_TuneCP5_13p6TeV_pythia8
  ZprimeToQQ_M300_TuneCP5_13p6TeV_pythia8
  ZprimeToQQ_M400_TuneCP5_13p6TeV_pythia8
  ZprimeToQQ_M500_TuneCP5_13p6TeV_pythia8
)

# Create list of EDM files for pileup sample
PILEUP_FILELIST="${THIS_DIR}"/../data/Neutrino_E10_gun_RunIIISummer24_PREMIX.txt
[ -f "${PILEUP_FILELIST}" ] || "${THIS_DIR}"/../data/create_files.sh

NUMTHREADS=4
JOBFLAVOUR=longlunch

for SAMPLE_LABEL in "${SAMPLE_LABELS[@]}"; do

  bdriverStepChain \
   -w "${THIS_DIR}"/../wfs/wf_ZprimeToQQ_TuneCP5_13p6TeV_pythia8.json \
   -f "${THIS_DIR}"/../fragments/fragment_"${SAMPLE_LABEL}".py \
   -p filelist:"${PILEUP_FILELIST}" \
   -o "${OUT_DIR}"/"${SAMPLE_LABEL}" \
   -d "${OUT_DIR}"/"${SAMPLE_LABEL}"/cmssw_areas \
   --output-dir-cmsRun "${OUT_DIR_CMSRUN}"/"${SAMPLE_LABEL}" \
   --os "${SCRAM_ARCH::3}" --JobFlavour "${JOBFLAVOUR}" --cpus "${NUMTHREADS}" \
   -l 1 -j 4000 -n 250
done
