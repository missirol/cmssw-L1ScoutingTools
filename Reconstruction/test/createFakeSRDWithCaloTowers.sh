#!/bin/bash -ex

JOB_LABEL=tmp2

TEST_DIR=$(cd $(dirname -- "${BASH_SOURCE[0]}") && pwd)

# Step 1:
#  create a NanoAOD file (using the "L1DPG"-Nano flavour to include CaloTower-related information)
#  [input data: run-398183, LSs 261-280 (L~2.2E34, PU~64)].
cat <<@EOF >> filein.txt
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/1918ed19-9688-47a4-9f2e-43ccd28f1b4a.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/d17a6148-87c0-46c0-a3c4-a1cf7bcb53cf.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/8107eb10-8a54-4cd9-95a3-06e7e72c4da7.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/60cb7953-a1d0-445f-87c1-150e59db673f.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/7b0dee26-e017-43e6-9bcb-8c0caec58f7b.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/3d9e95cd-2cf6-46b8-83a8-96a8727beb8e.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/66fadc8b-cde6-47e2-85c5-143adf227938.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/bdac0254-49a4-4baa-9081-4a461b044a27.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/5638c8cf-8222-4fc6-8d88-a608fc02d32c.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/0cefa074-cc10-4e91-b5df-7d117716a308.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/d002a71f-44f9-4a40-9053-9aa23cf4bb00.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/de2c0d35-3c26-435e-a34d-038cf519d804.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/4713367f-0db2-4ae5-8c4f-70ee8e496b29.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/e9951d6f-eadb-4bda-893b-e232db0a16d2.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/528f5f59-653b-4707-b253-30316e8caf9e.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/7a901ce4-fad2-49f0-80fc-b5f394c2d3ca.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/decce679-0d65-486d-959f-5377971e4d03.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/da04c290-78a7-4f54-aa27-d8033e70d54e.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/3d1c3210-24e1-4082-b683-2585d52a320d.root
/store/data/Run2025G/EphemeralZeroBias0/RAW/v1/000/398/183/00000/89e877c3-c417-476d-a885-54ec760309c7.root
@EOF

COMMON_OPTS=" --filein filelist:filein.txt"
COMMON_OPTS+=" --data --conditions 160X_dataRun3_HLT_v1 --geometry DB:Extended"
COMMON_OPTS+=" --scenario pp --era Run3_2025"
COMMON_OPTS+=" --datatier NANOAOD --eventcontent NANOAOD"
COMMON_OPTS+=" --nThreads 32 --nStreams 0"
COMMON_OPTS+=" --no_exec"

cmsDriver.py "${JOB_LABEL}" --process TEST ${COMMON_OPTS} \
  --python_filename "${JOB_LABEL}"_step1_cfg.py --fileout file:"${JOB_LABEL}"_step1_out.root \
  -s RAW2DIGI,NANO:@L1DPG -n 5440

edmConfigDump --prune "${JOB_LABEL}"_step1_cfg.py > "${JOB_LABEL}"_step1_cfg_dump.py
rm -rf "${JOB_LABEL}"_step1_cfg.py

cmsRun "${JOB_LABEL}"_step1_cfg_dump.py \
  2>&1 | tee "${JOB_LABEL}"_step1.log

# Step 2:
#  convert the CaloTower-related branches to FRD files
"${TEST_DIR}"/caloTowerUnpacker/testL1ScoutCaloTowerUnpacker_convertToFRD.py \
  -i "${JOB_LABEL}"_step1_out.root -l L1EmulCaloTower -n 10 \
  2>&1 | tee "${JOB_LABEL}"_step2.log

# Step 3:
#  convert the output of step-2 into a single EDM file in ROOT format
cmsRun "${TEST_DIR}"/l1sRepackSRD_cfg.py \
  --buBaseDirsNumStreams 1 \
  -n -1 \
  --repeat 100 \
  -i run398183 \
  -o "${JOB_LABEL}"_step3_out.root \
  2>&1 | tee "${JOB_LABEL}"_step3.log
