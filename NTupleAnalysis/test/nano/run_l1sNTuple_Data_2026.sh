#!/bin/bash -e

if [ $# -eq 1 ]; then
  ODIR1="${1}"
  ODIR2="${1}"
elif [ $# -eq 2 ]; then
  ODIR1="${1}"
  ODIR2="${2}"
else
  printf "%s\n" "--------------------------------------------------"
  printf "%s\n" " >>> FATAL -- at least 1 input argument required:"
  printf "%s\n" "     [1] path to output logs, and"
  printf "%s\n" "     [2] path to output files (same as [1] if not specified)."
  printf "%s\n" "--------------------------------------------------"
  exit 1
fi

if [ -d "${ODIR1}" ]; then
  printf "%s\n" " >>> FATAL -- target output directory already exists: ${ODIR1}"
  exit 1
fi

if [ -d "${ODIR2}" ]; then
  printf "%s\n" " >>> FATAL -- target output directory already exists: ${ODIR2}"
  exit 1
fi

mkdir -p "${ODIR1}"/jsons
JSON_LABEL="${ODIR1}"/jsons/l1sCaloTowersJson2026

CMSDRIVER_COMMON_OPTS="""
 --era Run3_2026 --scenario pp \
 --data --conditions 160X_dataRun3_Prompt_v1 --geometry DB:Extended \
 --process NANO --datatier NANOAOD --eventcontent NANOAOD \
 --filein tmp1.root --fileout tmp2.root \
 --no_exec
"""

# Create grid-certificate proxy (if not already in place)
if [ ! -f "${X509_USER_PROXY}" ]; then
  voms-proxy-init --voms cms --rfc --valid 168:00
fi

###
### JSON files for Run/LS selection
###
rm -f "${JSON_LABEL}"_json1819_pp2026_certCaloOnly.json
wget https://cernbox.cern.ch/remote.php/dav/public-files/Dxdcs0XwLwuH5z8/\
json1819_pp2026_certCaloOnly.json \
  -O "${JSON_LABEL}"_json1819_pp2026_certCaloOnly.json

l1sCaloTowersJson2026 \
  -i "${JSON_LABEL}"_json1819_pp2026_certCaloOnly.json \
  --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_BRIL.json \
  -o "${JSON_LABEL}" -v

LUMIJSON_L1S_SE="${JSON_LABEL}"_L1ScoutingSelection_Run2026D_goodWithoutReReco.json

###
### Function to create batch-jobs area
###
create_bjobs_areas () {
  cmsDriver.py none ${CMSDRIVER_COMMON_OPTS} -s "${CMSDRIVER_STEPS}" \
    --python_filename .tmp_cfg.py

  edmConfigDump --prune .tmp_cfg.py > .tmp_cfg_dump.py

  [ ! -z ${RUNLIST} ] || RUNLIST=$(python3 -c """\
import json
run_dict = json.load(open('${LUMIJSON}'))
for runNumber in sorted(run_dict.keys()):
    print(runNumber)
""")

  echo "--------------------------------------------------"
  for sampleKey in ${!SAMPLES_MAP[@]}; do
    sampleName=${SAMPLES_MAP[${sampleKey}]}
    for runNumber in ${RUNLIST[@]}; do
      bdriver -c .tmp_cfg_dump.py \
        --customize-cfg \
        --data \
        -m -1 \
        -n "${JOB_MAX_NEVENTS}" \
        -r "${JOB_REPORTEVERY}" \
        --json "${LUMIJSON}" \
        --run "${runNumber}" \
        --cpus "${NTHREADS_PER_JOB}" \
        --JobFlavour "${JOB_HTC_FLAVOUR}" \
        --os "${SCRAM_ARCH::3}" \
        -d "${sampleName}" \
        -p 0 \
        -o "${ODIR1}"/"${sampleKey}"/run"${runNumber}" \
        --output-dir-cmsRun "${ODIR2}"/"${sampleKey}"/run"${runNumber}" \
        --output-file-prefix "${sampleKey}"
      echo "--------------------------------------------------"
    done
  done
  cp -p "${LUMIJSON}" "${ODIR2}"/"${sampleKey}"
  unset sampleKey sampleName runNumber RUNLIST
  rm -rf .tmp_cfg{,_dump}.py __pycache__
}

###
### Data: L1ScoutingSelection.
###  - Main data set for physics analysis.
###
declare -A SAMPLES_MAP
SAMPLES_MAP["L1ScoutingSelection_Run2026D"]="/L1ScoutingSelection/Run2026D-v1/L1SCOUT"
CMSDRIVER_STEPS=NANO:@L1ScoutReRecoOnlyJetsSelect
LUMIJSON="${LUMIJSON_L1S_SE}"
NTHREADS_PER_JOB=4
JOB_MAX_NEVENTS=150000
JOB_REPORTEVERY=1500
JOB_HTC_FLAVOUR=longlunch
create_bjobs_areas
unset SAMPLES_MAP

###
### Data: L1Scouting.
###  - Processing only data from one run to measure
###    the efficiency of the dijet online selection.
###
declare -A SAMPLES_MAP
SAMPLES_MAP["L1Scouting_Run2026D"]="/L1Scouting/Run2026D-v1/L1SCOUT"
CMSDRIVER_STEPS=NANO:@L1ScoutReRecoOnlyJets
LUMIJSON="${LUMIJSON_L1S_SE}"
RUNLIST=(403937)
NTHREADS_PER_JOB=4
JOB_MAX_NEVENTS=150000
JOB_REPORTEVERY=1500
JOB_HTC_FLAVOUR=longlunch
create_bjobs_areas
unset SAMPLES_MAP

###
### Data: HLTPhysics
###  - Data containing full-event content (RAW) and only "fat" events with
###    extra L1T-related information (e.g. CaloTowers from the CaloL1 FEDs).
###    Used to validate the content of the L1Scouting data sets.
###
declare -A SAMPLES_MAP
SAMPLES_MAP["HLTPhysics_Run2026D"]="/HLTPhysics/Run2026D-v1/RAW"
CMSDRIVER_STEPS=RAW2DIGI,NANO:@L1DPG
LUMIJSON="${LUMIJSON_L1S_SE}"
NTHREADS_PER_JOB=4
JOB_MAX_NEVENTS=-1
JOB_REPORTEVERY=1000
JOB_HTC_FLAVOUR=espresso
create_bjobs_areas
unset SAMPLES_MAP
