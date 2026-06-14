#!/bin/bash -e

ODIR1=tmpout
ODIR2=tmpout

JOB_LABEL=l1sReNano

COMMON_OPTS="""
 -n -1
 --geometry DB:Extended \
 --scenario pp --era Run3_2026 \
 --data --conditions 160X_dataRun3_Prompt_v1 \
 --process NANO --datatier NANOAOD --eventcontent NANOAOD \
 --filein tmp1.root --fileout tmp2.root \
 --nStreams 0 \
 --no_exec
"""

###
### JSON files for Run/LS selection
###
cat <<@EOF > tmp_lumi.json
{ "402512": [[300,300]], "403937": [[500,500]] }
@EOF

###
### Job Submission Function
###
create_bjobs_areas () {
  cmsDriver.py none ${COMMON_OPTS} -s "${CMSDRIVER_STEPS}" \
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
      --json "${JSON_FILE}" \
      --cpus "${NTHREADS_PER_JOB}" \
      --JobFlavour "${JOB_HTC_FLAVOUR}" \
      -d "${sampleName}" \
      -p 0 \
      -o "${ODIR1}"/"${sampleKey}" \
      --output-dir-cmsRun "${ODIR2}"/"${sampleKey}"
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
JSON_FILE=tmp_lumi.json
NTHREADS_PER_JOB=8
JOB_MAX_NEVENTS=2500
JOB_HTC_FLAVOUR=microcentury

create_bjobs_areas

###
### Data: L1ScoutingSelection
###
declare -A samplesMap
samplesMap["L1ScoutingSelection_Run2026D"]="/L1ScoutingSelection/Run2026D-v1/L1SCOUT"

CMSDRIVER_STEPS=NANO:@L1ScoutReRecoSelect
JSON_FILE=tmp_lumi.json
NTHREADS_PER_JOB=8
JOB_MAX_NEVENTS=7500
JOB_HTC_FLAVOUR=microcentury

create_bjobs_areas

###
### Data: HLTPhysics
###
declare -A samplesMap
samplesMap["HLTPhysics_Run2026B"]="/HLTPhysics/Run2026B-v1/RAW"
samplesMap["HLTPhysics_Run2026D"]="/HLTPhysics/Run2026D-v1/RAW"

CMSDRIVER_STEPS=RAW2DIGI,NANO:@L1DPG
JSON_FILE=tmp_lumi.json
NTHREADS_PER_JOB=8
JOB_MAX_NEVENTS=-1
JOB_HTC_FLAVOUR=espresso

create_bjobs_areas

###
### Final cleanup
###
rm -rf tmp_lumi.json
