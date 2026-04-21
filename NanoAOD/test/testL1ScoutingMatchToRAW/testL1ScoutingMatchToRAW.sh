#!/bin/bash -ex

JOB_LABEL=tmp_testL1ScoutingMatchToRAW

TEST_DIR=$(cd $(dirname -- "${BASH_SOURCE[0]}") && pwd)

#INPUTFILE_STEP1=file:/eos/cms/tier0/store/data/Run2026B/JetMET0/RAW/v1/000/401/848/00000/0a458857-1e43-401d-b429-3a90d2df7e48.root
INPUTFILE_STEP1=file:/eos/cms/tier0/store/data/Run2026B/HLTPhysics/RAW/v1/000/402/144/00000/6e1300de-1e8c-42da-9f6f-7d7080eaaed5.root
INPUTFILE_STEP2=file:/eos/cms/tier0/store/data/Run2026B/L1Scouting/L1SCOUT/v1/000/402/144/00000/56c150ff-0b37-4980-9b9a-547985d36a66.root

MAX_EVENTS=10
MAX_ORBITS=10

COMMON_OPTS="--data --conditions 160X_dataRun3_Prompt_v1 --geometry DB:Extended"
COMMON_OPTS+=" --scenario pp --era Run3_2026"
COMMON_OPTS+=" --datatier NANOAOD --eventcontent NANOAOD"
COMMON_OPTS+=" --nThreads 8 --nStreams 0"

# Step 1:
#  create a NanoAOD file (using the "L1DPG"-Nano flavour to include CaloTower-related information)
#  [input data: run-401848, LSs 720-721].
cmsDriver.py "${JOB_LABEL}" --process TEST ${COMMON_OPTS} \
  --filein "${INPUTFILE_STEP1}" \
  --python_filename "${JOB_LABEL}"_step1_cfg.py \
  --fileout file:"${JOB_LABEL}"_step1_out.root \
  -s RAW2DIGI,NANO:@L1DPG -n "${MAX_EVENTS}" \
  2>&1 | tee "${JOB_LABEL}"_step1.log

# Step 2:
#  create a NanoAOD file from L1Scouting data
#  [input data: run-401848, LSs 720-721].
cmsDriver.py "${JOB_LABEL}" --process TEST ${COMMON_OPTS} \
  --filein "${INPUTFILE_STEP2}" \
  --python_filename "${JOB_LABEL}"_step2_cfg.py \
  --fileout file:"${JOB_LABEL}"_step2_out.root \
  -s NANO:@L1Scout -n "${MAX_ORBITS}" \
  --customise PhysicsTools/NanoAOD/custom_l1scoutingrun3_cff.addHardwareValues \
  2>&1 | tee "${JOB_LABEL}"_step2.log

rm -rf __pycache__

#  --no_exec
#
##cat <<@EOF >> "${JOB_LABEL}"_step2_cfg.py
##process.source.eventsToProcess = cms.untracked.VEventRange(
##    '401848:710:185861736',
##    '401848:710:185864208',
##    '401848:710:185864883',
##    '401848:710:185865108',
##    '401848:710:185866008',
##    '401848:710:185866233',
##    '401848:710:185868138',
##    '401848:710:185869035',
##    '401848:710:185872290',
##    '401848:710:185872402',
##)
##@EOF
#
#cmsRun "${JOB_LABEL}"_step2_cfg.py \
