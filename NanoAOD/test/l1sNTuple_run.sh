#!/bin/bash -e

if [ $# -lt 1 ]; then
  printf "\n%s\n\n" ">> ERROR: input argument missing - specify path to output directory"
  exit 1
fi

# number of events per sample
NEVT=5000000

if [ $# -eq 1 ]; then
  ODIR=${1}
#  ODIR_cmsRun=$1
else
  ODIR=${1}
#  ODIR_cmsRun=${2}
fi

if [ -d ${ODIR} ]; then
  printf "%s\n" "output directory already exists: ${ODIR}"
  exit 1
fi

declare -A samplesMap

# QCD Pt-Flat
samplesMap["Run3Winter25_QCD_PtFlat15to7000_13p6TeV_FlatPU0to120"]="/QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/Run3Winter25Digi-FlatPU0to120_142X_mcRun3_2025_realistic_v9-v4/GEN-SIM-RAW"

# options (JobFlavour and AccountingGroup)
opts="--JobFlavour microcentury"

COMMON_OPTS=" --filein tmp.root"
COMMON_OPTS+=" --mc --conditions auto:phase1_2025_realistic --geometry DB:Extended"
COMMON_OPTS+=" --scenario pp --era Run3_2025"
COMMON_OPTS+=" --datatier NANOAOD --eventcontent NANOAOD"
COMMON_OPTS+=" --nThreads 8 --nStreams 0"
COMMON_OPTS+=" --no_exec"

JOB_LABEL=nanoL1TCustom
cmsDriver.py "${JOB_LABEL}" --process "${JOB_LABEL^^}" ${COMMON_OPTS} \
  --python_filename "${JOB_LABEL}"_cfg.py --fileout file:"${JOB_LABEL}"_out.root \
  -s RAW2DIGI,NANO:@GENLite+@L1ScoutCaloTowersMC \
  -n 1

cat <<@EOF >> "${JOB_LABEL}"_cfg.py
process.NANOAODoutput.saveTriggerResults = cms.untracked.bool(False)
@EOF

edmConfigDump --prune "${JOB_LABEL}"_cfg.py > "${JOB_LABEL}"_cfg_dump.py

rm -rf "${JOB_LABEL}"_cfg.py __pycache__

for sampleKey in ${!samplesMap[@]}; do
  sampleName=${samplesMap[${sampleKey}]}

  # number of events per sample
  numEvents=${NEVT}

  bdriver -c "${JOB_LABEL}"_cfg_dump.py --customize-cfg -m ${numEvents} -n 1000 --cpus 8 --mem 1000 --time 600 ${opts} \
    -d ${sampleName} -p 0 -o ${ODIR}/${sampleKey}
done
unset sampleKey numEvents sampleName

rm -f "${JOB_LABEL}"_cfg_dump.py

unset opts samplesMap NEVT ODIR #ODIR_cmsRun
