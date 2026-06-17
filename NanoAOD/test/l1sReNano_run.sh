#!/bin/bash -e

if [ $# -ne 2 ]; then
  printf "%s\n" "--------------------------------------------------"
  printf "%s\n" " >>> FATAL -- 2 input arguments required:"
  printf "%s\n" "     (1) path to output logs, and"
  printf "%s\n" "     (2) path to output files!"
  printf "%s\n" "--------------------------------------------------"
  exit 1
fi

ODIR1="${1}"
ODIR2="${2}"

JOB_LABEL=l1sReNano

CMSDRIVER_COMMON_OPTS="""
 --era Run3_2026 --scenario pp \
 --data --conditions 160X_dataRun3_Prompt_v1 --geometry DB:Extended \
 --process NANO --datatier NANOAOD --eventcontent NANOAOD \
 --filein tmp1.root --fileout tmp2.root \
 --no_exec
"""

###
### JSON files for Run/LS selection
###
rm -f json1819_pp2026_certCaloOnly.json
wget https://cernbox.cern.ch/remote.php/dav/public-files/Dxdcs0XwLwuH5z8/\
json1819_pp2026_certCaloOnly.json

l1sCaloTowersJson2026 -i json1819_pp2026_certCaloOnly.json \
  --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_BRIL.json \
  -o l1sCaloTowersJson2026 -v

LUMIJSON_L1S_ZB=l1sCaloTowersJson2026_L1Scouting_goodWithReReco.json
LUMIJSON_L1S_SE=l1sCaloTowersJson2026_L1ScoutingSelection_goodWithReReco.json

##!!
##!! Temporary: use hand-made JSON file to
##!! process only a small subset of the data
##!!
cat <<@EOF > tmp_lumi.json
{
  "402512": [[300, 300]],
  "403441": [[100, 100]],
  "403937": [[501, 550]]
}
@EOF
LUMIJSON_L1S_ZB=tmp_lumi.json
LUMIJSON_L1S_SE=tmp_lumi.json

###
### Job Submission Function
###
create_bjobs_areas () {
  cmsDriver.py none ${CMSDRIVER_COMMON_OPTS} -s "${CMSDRIVER_STEPS}" \
    --python_filename "${JOB_LABEL}"_cfg.py

  edmConfigDump --prune "${JOB_LABEL}"_cfg.py > "${JOB_LABEL}"_cfg_dump.py

  echo "--------------------------------------------------"
  for sampleKey in ${!samplesMap[@]}; do
    sampleName=${samplesMap[${sampleKey}]}
    bdriver -c "${JOB_LABEL}"_cfg_dump.py \
      --customize-cfg \
      --data \
      -m -1 \
      -n "${JOB_MAX_NEVENTS}" \
      --json "${LUMIJSON}" \
      --cpus "${NTHREADS_PER_JOB}" \
      --JobFlavour "${JOB_HTC_FLAVOUR}" \
      -d "${sampleName}" \
      -p 0 \
      -o "${ODIR1}"/"${sampleKey}" \
      --output-dir-cmsRun "${ODIR2}"/"${sampleKey}" \
      --output-file-prefix "${sampleKey}"
    echo "--------------------------------------------------"
  done
  unset sampleKey sampleName samplesMap
  rm -rf "${JOB_LABEL}"_cfg{,_dump}.py __pycache__
}

###
### Data: L1Scouting
###
declare -A samplesMap
samplesMap["L1Scouting_Run2026B"]="/L1Scouting/Run2026B-v1/L1SCOUT"
samplesMap["L1Scouting_Run2026D"]="/L1Scouting/Run2026D-v1/L1SCOUT"

CMSDRIVER_STEPS=NANO:@L1ScoutReReco
LUMIJSON="${LUMIJSON_L1S_ZB}"
NTHREADS_PER_JOB=8
JOB_MAX_NEVENTS=-1
JOB_HTC_FLAVOUR=workday

create_bjobs_areas

###
### Data: L1ScoutingSelection
###
declare -A samplesMap
samplesMap["L1ScoutingSelection_Run2026D"]="/L1ScoutingSelection/Run2026D-v1/L1SCOUT"

CMSDRIVER_STEPS=NANO:@L1ScoutReRecoSelect
LUMIJSON="${LUMIJSON_L1S_SE}"
NTHREADS_PER_JOB=8
JOB_MAX_NEVENTS=50000
JOB_HTC_FLAVOUR=longlunch

create_bjobs_areas

###
### Data: HLTPhysics
###
declare -A samplesMap
samplesMap["HLTPhysics_Run2026B"]="/HLTPhysics/Run2026B-v1/RAW"
samplesMap["HLTPhysics_Run2026D"]="/HLTPhysics/Run2026D-v1/RAW"

CMSDRIVER_STEPS=RAW2DIGI,NANO:@L1DPG
LUMIJSON="${LUMIJSON_L1S_ZB}"
NTHREADS_PER_JOB=8
JOB_MAX_NEVENTS=-1
JOB_HTC_FLAVOUR=espresso

create_bjobs_areas
