#!/bin/bash -ex

JOB_LABEL=tmp_testL1ScoutingMatchToRAW_TestEnablesEcalHcal

TEST_DIR=$(cd $(dirname -- "${BASH_SOURCE[0]}") && pwd)

INPUTFILE_STEP1=file:/eos/cms/tier0/store/data/Run2026B/TestEnablesEcalHcal/RAW/Express-v1/000/401/848/00000/bf067676-cc2a-48a6-a8cb-e999e4d30869.root

MAX_EVENTS=-1

COMMON_OPTS="--data --conditions 160X_dataRun3_Prompt_v1 --geometry DB:Extended"
COMMON_OPTS+=" --scenario pp --era Run3_2026"
COMMON_OPTS+=" --datatier NANOAOD --eventcontent NANOAOD"
COMMON_OPTS+=" --nThreads 8 --nStreams 0"

## Step 1: create a NanoAOD file using the "L1DPG"-Nano flavour
##  to include CaloTower-related information
##  [input data: run-401848, LSs 710].
cat <<@EOF > "${JOB_LABEL}"_step1.json
{ "401848": [[710,711]] }
@EOF

cmsDriver.py "${JOB_LABEL}" --process TEST ${COMMON_OPTS} \
  --filein "${INPUTFILE_STEP1}" \
  --python_filename "${JOB_LABEL}"_step1_cfg.py \
  --fileout file:"${JOB_LABEL}"_step1_out.root \
  --lumiToProcess "${JOB_LABEL}"_step1.json \
  -s RAW2DIGI,NANO:@L1DPG -n "${MAX_EVENTS}" \
  --dump_python

cat <<@EOF >> "${JOB_LABEL}"_step1_cfg.py

process.ecalDigis.InputLabel = 'hltEcalCalibrationRaw'
process.hcalDigis.InputLabel = 'hltHcalCalibrationRaw'

process.customTask = cms.Task(
    process.ecalDigis,
    process.hcalDigis,
    process.simCaloStage2Layer1Digis,
    process.l1EmulCaloTowerTable,
)

process.customSequence = cms.Sequence(process.customTask)

process.customPath = cms.Path(process.customSequence)

process.schedule = cms.Schedule(
    process.customPath,
    process.NANOAODoutput_step
)
@EOF

cmsRun "${JOB_LABEL}"_step1_cfg.py \
  2>&1 | tee "${JOB_LABEL}"_step1.log

rm -rf __pycache__
