#!/bin/bash -ex

JOB_LABEL=ref

TEST_DIR=$(cd $(dirname -- "${BASH_SOURCE[0]}") && pwd)

INPUTFILE_STEP1=/store/data/Run2026D/HLTPhysics/RAW/v1/000/403/663/00000/4c59dbec-3e8d-4924-b112-798625943232.root

cat <<@EOF > tmp.json
{ "403663": [[43, 53]] }
@EOF

cmsDriver.py "${JOB_LABEL}" --process TEST \
  --data --conditions 160X_dataRun3_Prompt_v1 --geometry DB:Extended \
  --scenario pp --era Run3_2026 \
  --datatier NANOAOD --eventcontent NANOAOD \
  --nThreads 8 --nStreams 0 \
  --lumiToProcess tmp.json \
  --filein "${INPUTFILE_STEP1}" \
  --python_filename "${JOB_LABEL}"_step1_cfg.py \
  --fileout file:"${JOB_LABEL}"_step1_out.root \
  -s RAW2DIGI,NANO:@L1DPG -n -1 \
  2>&1 | tee "${JOB_LABEL}"_step1.log

rm -rf tmp.json __pycache__
