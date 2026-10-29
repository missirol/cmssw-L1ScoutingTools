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

JOB_LABEL=tmp_l1sNTuple

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
rm -f json1819_pp2026_certCaloOnly.json
wget https://cernbox.cern.ch/remote.php/dav/public-files/Dxdcs0XwLwuH5z8/\
json1819_pp2026_certCaloOnly.json \
  -O tmp_json1819_pp2026_certCaloOnly.json

l1sCaloTowersJson2026 \
  -i tmp_json1819_pp2026_certCaloOnly.json \
  --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_BRIL.json \
  -o "${JOB_LABEL}" -v

#LUMIJSON_L1S_ZB="${JOB_LABEL}"_L1Scouting_goodWithReReco.json
LUMIJSON_L1S_SE="${JOB_LABEL}"_L1ScoutingSelection_Run2026D_goodWithoutReReco.json

###
### Job Submission Function
###
create_bjobs_areas () {
  cmsDriver.py none ${CMSDRIVER_COMMON_OPTS} -s "${CMSDRIVER_STEPS}" \
    --python_filename "${JOB_LABEL}"_cfg.py

  edmConfigDump --prune "${JOB_LABEL}"_cfg.py > "${JOB_LABEL}"_cfg_dump.py

  RUNLIST=$(python3 -c """
import json
run_dict = json.load(open('${LUMIJSON}'))
for runNumber in sorted(run_dict.keys()):
    print(runNumber)
""")

  echo "--------------------------------------------------"
  for sampleKey in ${!samplesMap[@]}; do
    sampleName=${samplesMap[${sampleKey}]}
    for runNumber in ${RUNLIST[@]}; do
      bdriver -c "${JOB_LABEL}"_cfg_dump.py \
        --customize-cfg \
        --data \
        -m -1 \
        -n "${JOB_MAX_NEVENTS}" \
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
  unset sampleKey sampleName samplesMap runNumber
  rm -rf "${JOB_LABEL}"_cfg{,_dump}.py __pycache__
}

# ###
# ### Data: L1Scouting
# ###
# declare -A samplesMap
# samplesMap["L1Scouting_Run2026B"]="/L1Scouting/Run2026B-v1/L1SCOUT"
# samplesMap["L1Scouting_Run2026D"]="/L1Scouting/Run2026D-v1/L1SCOUT"
#
# CMSDRIVER_STEPS=NANO:@L1ScoutReReco
# LUMIJSON="${LUMIJSON_L1S_ZB}"
# NTHREADS_PER_JOB=8
# JOB_MAX_NEVENTS=-1
# JOB_HTC_FLAVOUR=workday
#
# create_bjobs_areas

###
### Data: L1ScoutingSelection
###
declare -A samplesMap
samplesMap["L1ScoutingSelection_Run2026D"]="/L1ScoutingSelection/Run2026D-v1/L1SCOUT"

CMSDRIVER_STEPS=NANO:@L1ScoutReRecoOnlyJetsSelect
LUMIJSON="${LUMIJSON_L1S_SE}"
NTHREADS_PER_JOB=4
JOB_MAX_NEVENTS=150000
JOB_HTC_FLAVOUR=longlunch

create_bjobs_areas

# ###
# ### Data: HLTPhysics
# ###
# declare -A samplesMap
# samplesMap["HLTPhysics_Run2026B"]="/HLTPhysics/Run2026B-v1/RAW"
# samplesMap["HLTPhysics_Run2026D"]="/HLTPhysics/Run2026D-v1/RAW"
#
# CMSDRIVER_STEPS=RAW2DIGI,NANO:@L1DPG
# LUMIJSON="${LUMIJSON_L1S_ZB}"
# NTHREADS_PER_JOB=8
# JOB_MAX_NEVENTS=-1
# JOB_HTC_FLAVOUR=espresso
#
# create_bjobs_areas
