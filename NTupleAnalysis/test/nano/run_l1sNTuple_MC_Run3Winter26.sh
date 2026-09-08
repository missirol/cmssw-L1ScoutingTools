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

JOB_LABEL=tmp_l1sNTuple

# number of events per sample
NEVT=5000000

# number of CPUs per HT-Condor job
# (same as number of threads and
# CMSSW streams per cmsRun job)
NTHREADS_PER_JOB=8

declare -A samplesMap

# QCD Pt-Flat
samplesMap["Run3Winter25_QCD_PtFlat15to7000_13p6TeV_EpsilonPU"]="/QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/Run3Winter25Digi-EpsilonPU_142X_mcRun3_2025_realistic_v9-v4/GEN-SIM-RAW"
samplesMap["Run3Winter25_QCD_PtFlat15to7000_13p6TeV_FlatPU0to120"]="/QCD_Bin-PT-15to7000_Par-PT-flat2022_TuneCP5_13p6TeV_pythia8/Run3Winter25Digi-FlatPU0to120_142X_mcRun3_2025_realistic_v9-v4/GEN-SIM-RAW"
samplesMap["Run3Winter25_TTbar_13p6TeV"]="/TT_TuneCP5_13p6TeV_powheg-pythia8/Run3Winter25Digi-142X_mcRun3_2025_realistic_v7-v2/GEN-SIM-RAW"

# Options for job submission (e.g. JobFlavour)
JOB_HTC_FLAVOUR="microcentury"

COMMON_OPTS=" --filein tmp.root"
COMMON_OPTS+=" --mc --conditions auto:phase1_2025_realistic --geometry DB:Extended"
COMMON_OPTS+=" --scenario pp --era Run3_2025"
COMMON_OPTS+=" --datatier NANOAOD --eventcontent NANOAOD"
COMMON_OPTS+=" --nThreads ${NTHREADS_PER_JOB} --nStreams 0"
COMMON_OPTS+=" --no_exec"

cmsDriver.py "${JOB_LABEL}" --process NANO ${COMMON_OPTS} \
  --python_filename "${JOB_LABEL}"_cfg.py --fileout file:"${JOB_LABEL}"_out.root \
  -s RAW2DIGI,NANO:@GENLite+@L1ScoutCaloTowersMC \
  -n 1

cat <<@EOF >> "${JOB_LABEL}"_cfg.py
process.NANOAODoutput.outputCommands += ['drop edmTriggerResults_*_*_*']
@EOF

edmConfigDump --prune "${JOB_LABEL}"_cfg.py > "${JOB_LABEL}"_cfg_dump.py

rm -rf "${JOB_LABEL}"_cfg.py __pycache__

for sampleKey in ${!samplesMap[@]}; do
  sampleName=${samplesMap[${sampleKey}]}

  bdriver -c "${JOB_LABEL}"_cfg_dump.py \
    --customize-cfg \
    -m "${NEVT}" \
    -n 1000 \
    --cpus "${NTHREADS_PER_JOB}" \
    --mem 1000 \
    --time 600 \
    -d "${sampleName}" \
    -p 0 \
    --JobFlavour "${JOB_HTC_FLAVOUR}" \
    -o "${ODIR1}"/"${sampleKey}" \
    --output-dir-cmsRun "${ODIR2}"/"${sampleKey}"
done

rm -f "${JOB_LABEL}"_cfg_dump.py
