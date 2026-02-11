#!/bin/bash -ex

# Step 1:
#  create a NanoAOD file using the "L1DPG"-Nano flavour
#  to include CaloTower-related information
INPUT_FILE=/store/data/Run2025G/ZeroBias/RAW/v1/000/398/903/00000/e74e0798-0eb4-470f-b5d3-5d4fe0b3efbe.root
RUN_NUMBER=398903

TEST_DIR=$(cd $(dirname -- "${BASH_SOURCE[0]}") && pwd)

JOB_LABEL=tmp_testL1ScoutCaloTowers

COMMON_OPTS=" --filein ${INPUT_FILE}"
COMMON_OPTS+=" --data --conditions 160X_dataRun3_HLT_v1"
COMMON_OPTS+=" --scenario pp --era Run3_2025"
COMMON_OPTS+=" --datatier NANOAOD --eventcontent NANOAOD"
COMMON_OPTS+=" --nThreads 1 --nStreams 0"
COMMON_OPTS+=" --no_exec"

cmsDriver.py "${JOB_LABEL}" --process TEST ${COMMON_OPTS} \
  --python_filename "${JOB_LABEL}"_cfg.py --fileout file:"${JOB_LABEL}"_out.root \
  -s RAW2DIGI,NANO:@L1DPG \
  -n 10

edmConfigDump --prune "${JOB_LABEL}"_cfg.py > "${JOB_LABEL}"_cfg_dump.py

cmsRun "${JOB_LABEL}"_cfg_dump.py 2>&1 | tee "${JOB_LABEL}"_cfg_dump.log

rm -rf "${JOB_LABEL}"_cfg.py

# Step 2:
#  convert the CaloTower-related branches to FRD files
"${TEST_DIR}"/convertL1NanoToL1ScoutCaloTowerFRD.py \
  -i "${JOB_LABEL}"_out.root -l L1EmulCaloTower -n 5

# Step 3:
#  process FRD files, perform the unpacking and jet-clustering of the CaloTowers
cmsRun "${TEST_DIR}"/testL1ScoutCaloTowerUnpacker_cfg.py \
  -r "${RUN_NUMBER}" -o "${JOB_LABEL}"_out2.root

rm -rf __pycache__
rm -rf tmp
