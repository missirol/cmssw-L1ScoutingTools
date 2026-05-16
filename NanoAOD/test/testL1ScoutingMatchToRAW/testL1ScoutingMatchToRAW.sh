#!/bin/bash -ex

JOB_LABEL=tmp_testL1ScoutingMatchToRAW

TEST_DIR=$(cd $(dirname -- "${BASH_SOURCE[0]}") && pwd)

#INPUTFILE_STEP1=file:/eos/cms/tier0/store/data/Run2026C/JetMET0/RAW/v1/000/403/166/00001/8ab703c0-46b2-4abf-b7be-c501ea778a77.root
#INPUTFILE_STEP2=file:/eos/cms/tier0/store/data/Run2026C/L1Scouting/L1SCOUT/v1/000/403/166/00000/cffde75a-eba8-4e06-b819-20458186d3d5.root
#
#cat <<@EOF > tmp.json
#{ "403166": [[1295, 1295]] }
#@EOF

INPUTFILE_STEP1=/store/data/Run2026D/HLTPhysics/RAW/v1/000/403/686/00000/23922806-3641-4341-85e1-7264b662740a.root
INPUTFILE_STEP2=filelist:files.txt

cat <<@EOF > tmp.json
{ "403686": [[185, 194]] }
@EOF

MAX_EVENTS=-1
MAX_ORBITS=-1

COMMON_OPTS="--data --conditions 160X_dataRun3_Prompt_v1 --geometry DB:Extended"
COMMON_OPTS+=" --scenario pp --era Run3_2026"
COMMON_OPTS+=" --datatier NANOAOD --eventcontent NANOAOD"
COMMON_OPTS+=" --nThreads 8 --nStreams 0"

# Step 1: create a NanoAOD file using the "L1DPG"-NanoAOD flavour
cmsDriver.py "${JOB_LABEL}" --process TEST ${COMMON_OPTS} \
  --lumiToProcess tmp.json \
  --filein "${INPUTFILE_STEP1}" \
  --python_filename "${JOB_LABEL}"_step1_cfg.py \
  --fileout file:"${JOB_LABEL}"_step1_out.root \
  -s RAW2DIGI,NANO:@L1DPG -n "${MAX_EVENTS}" \
  2>&1 | tee "${JOB_LABEL}"_step1.log

# Step 2: create a NanoAOD file from L1Scouting data
cmsDriver.py "${JOB_LABEL}" --process TEST ${COMMON_OPTS} \
  --lumiToProcess tmp.json \
  --filein "${INPUTFILE_STEP2}" \
  --python_filename "${JOB_LABEL}"_step2_cfg.py \
  --fileout file:"${JOB_LABEL}"_step2_out.root \
  -s NANO:@L1Scout -n "${MAX_ORBITS}" \
  --customise PhysicsTools/NanoAOD/custom_l1scoutingrun3_cff.addHardwareValues \
  --no_exec

cat <<@EOF >> tmp.py
#!/usr/bin/env python3
import ROOT
import sys

f0 = ROOT.TFile.Open(sys.argv[1])
t0 = f0.Get('Events')

print('process.source.eventsToProcess = cms.untracked.VEventRange(')

for evt in t0:
    bx = evt.bunchCrossing
    if bx % 9 not in [7, 8]:
        continue
    print(f"    '{evt.run}:{evt.luminosityBlock}:{evt.orbitNumber}',")

print(')')
@EOF
chmod u+x tmp.py
./tmp.py "${JOB_LABEL}"_step1_out.root >> "${JOB_LABEL}"_step2_cfg.py

cmsRun "${JOB_LABEL}"_step2_cfg.py

rm -rf tmp.json tmp.py __pycache__
