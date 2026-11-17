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

# For the L1Scouting (zero bias) and HLTPhysics primary data sets,
# one tenth of the LSs used for physics analysis are processed for
#  - measuring the efficiency of the dijet online filter (L1Scouting), and
#  - validating the CaloL1 content (CaloTowers) of the L1Scouting data set
#    by comparing it to that of the HLTPhysics data set.
LUMIJSON_L1S_ZB="${JSON_LABEL}"_L1ScoutingSelection_Run2026D_goodWithoutReReco_One10th.json

$(python3 -c """\
import json

def group_consecutive(nums):
    if not nums:
        return []

    sorted_nums = sorted(set(nums))
    groups = []
    start = end = sorted_nums[0]

    for n in sorted_nums[1:]:
        if n == end + 1:
            end = n
        else:
            groups.append([start, end])
            start = end = n

    groups.append([start, end])
    return groups

def expand(groups):
    result = set()
    for g in groups:
        result.update(range(g[0], g[-1] + 1))
    return result

inp_dict = json.load(open('${LUMIJSON_L1S_SE}'))
out_dict = {}
for runNumber in inp_dict:
    ls_list = sorted(list(expand(inp_dict[runNumber])))
    ls_list_len = len(ls_list)
    tmp_list = []
    for ls_idx in range(ls_list_len):
        ls_idx2 = ls_idx + ls_list_len//2
        while ls_idx2 >= ls_list_len:
            ls_idx2 -= ls_list_len
        if ls_idx % 50 == 0:
            tmp_list.append(ls_list[ls_idx2])
    out_dict[runNumber] = group_consecutive(tmp_list)

with open('${LUMIJSON_L1S_ZB}', 'w') as ofile:
    json.dump(out_dict, ofile, sort_keys=True, indent=4)
""")

###
### Function to create batch-jobs area
###
create_bjobs_areas () {
  cmsDriver.py none ${CMSDRIVER_COMMON_OPTS} -s "${CMSDRIVER_STEPS}" \
    --python_filename .tmp_cfg.py

  edmConfigDump --prune .tmp_cfg.py > .tmp_cfg_dump.py

  runList=$(python3 -c """\
import json
run_dict = json.load(open('${LUMIJSON}'))
for runNumber in sorted(run_dict.keys()):
    print(runNumber)
""")

  echo "--------------------------------------------------"
  for sampleKey in ${!SAMPLES_MAP[@]}; do
    sampleName=${SAMPLES_MAP[${sampleKey}]}
    for runNumber in ${runList[@]}; do
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
        --name "${sampleKey}"_run"${runNumber}" \
        -o "${ODIR1}"/"${sampleKey}"/run"${runNumber}" \
        --output-dir-cmsRun "${ODIR2}"/"${sampleKey}"/run"${runNumber}" \
        --output-file-prefix "${sampleKey}"
      echo "--------------------------------------------------"
    done
  done
  cp -p "${LUMIJSON}" "${ODIR2}"/"${sampleKey}"
  unset sampleKey sampleName runNumber runList
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
CMSDRIVER_STEPS=NANO:@L1ScoutReReco
LUMIJSON="${LUMIJSON_L1S_ZB}"
NTHREADS_PER_JOB=4
JOB_MAX_NEVENTS=10000
JOB_REPORTEVERY=1000
JOB_HTC_FLAVOUR=longlunch
create_bjobs_areas
unset SAMPLES_MAP

###
### Data: HLTPhysics.
###  - Data containing full-event content (RAW) and only "fat" events with
###    extra L1T-related information (e.g. CaloTowers from the CaloL1 FEDs).
###    Used to validate the content of the L1Scouting data sets.
###
declare -A SAMPLES_MAP
SAMPLES_MAP["HLTPhysics_Run2026D"]="/HLTPhysics/Run2026D-v1/RAW"
CMSDRIVER_STEPS=RAW2DIGI,NANO:@L1DPG
LUMIJSON="${LUMIJSON_L1S_ZB}"
NTHREADS_PER_JOB=4
JOB_MAX_NEVENTS=-1
JOB_REPORTEVERY=1000
JOB_HTC_FLAVOUR=espresso
create_bjobs_areas
unset SAMPLES_MAP
