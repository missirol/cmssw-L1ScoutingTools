#!/bin/bash -e

jobLabel=tmp_cmsDriver

nanoFlavours=(
  L1Scout
  L1ScoutSelect
)

declare -A inputFiles=(
  ["L1Scout"]="/store/data/Run2026B/L1Scouting/L1SCOUT/v1/000/402/144/00000/af07ed8c-d45e-41ad-81c7-8c32478c40be.root"
  ["L1ScoutSelect"]="/store/data/Run2026B/L1ScoutingSelection/L1SCOUT/v1/000/402/144/00000/56a86b0d-c4a0-4ffc-84c5-158494ec8ecc.root"
)

maxEvents=10

for nanoFlavour in "${nanoFlavours[@]}"; do
  dataTier=NANOAOD
  outputFilePrefix="${jobLabel}"_"${nanoFlavour}"_"${dataTier}"
  echo "--------------------------------------------------------------------------"
  echo "${outputFilePrefix}"
  echo "--------------------------------------------------------------------------"
  cmsDriver.py none -n "${maxEvents}" \
    --process "${dataTier}" --eventcontent "${dataTier}" --datatier "${dataTier}" \
    --era Run3_2026 --data --conditions auto:run3_data_prompt \
    --filein "${inputFiles[${nanoFlavour}]}" \
    --python_filename "${outputFilePrefix}".py \
    --fileout "${outputFilePrefix}".root \
    -s NANO:@"${nanoFlavour}"
  edmConfigDump --prune "${outputFilePrefix}".py > "${outputFilePrefix}"_dump.py
  edmFileUtil "${outputFilePrefix}".root

  dataTier=NANOEDMAOD
  outputFilePrefix="${jobLabel}"_"${nanoFlavour}"_"${dataTier}"
  echo "--------------------------------------------------------------------------"
  echo "${outputFilePrefix}"
  echo "--------------------------------------------------------------------------"
  cmsDriver.py none -n "${maxEvents}" \
    --process "${dataTier}" --eventcontent "${dataTier}" --datatier "${dataTier}" \
    --era Run3_2026 --data --conditions auto:run3_data_prompt \
    --filein "${inputFiles[${nanoFlavour}]}" \
    --python_filename "${outputFilePrefix}".py \
    --fileout "${outputFilePrefix}".root \
    -s NANO:@"${nanoFlavour}"
  edmConfigDump --prune "${outputFilePrefix}".py > "${outputFilePrefix}"_dump.py
  edmFileUtil "${outputFilePrefix}".root
  edmDumpEventContent "${outputFilePrefix}".root | tee "${outputFilePrefix}".txt

  # Conversion from NANOEDMAOD to NANOAOD with a hand-made config
cat <<@EOF >> "${outputFilePrefix}"_flattened1.py
import FWCore.ParameterSet.Config as cms

process = cms.Process("NANOAOD")

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring("file:${outputFilePrefix}.root")
)

process.outputModule = cms.OutputModule("OrbitNanoAODOutputModule",
    fileName = cms.untracked.string("file:${outputFilePrefix}_flattened1.root"),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAOD')
    ),
    selectedBx = cms.InputTag(""),
    skipEmptyBXs = cms.bool(True)
)

from Configuration.EventContent.EventContent_cff import L1SCOUTNANOAODEventContent
process.outputModule.update_(L1SCOUTNANOAODEventContent)

process.outputEndPath = cms.EndPath(process.outputModule)
@EOF
  cmsRun "${outputFilePrefix}"_flattened1.py 2>&1 | tee "${outputFilePrefix}"_flattened1.log
  edmFileUtil "${outputFilePrefix}"_flattened1.root

  # Conversion from NANOEDMAOD to NANOAOD using RunMerge.py
  runMergeFile="${CMSSW_BASE}"/src/Configuration/DataProcessing/test/RunMerge.py
  if [ ! -f "${runMergeFile}" ]; then
    runMergeFile="${CMSSW_RELEASE_BASE}"/src/Configuration/DataProcessing/test/RunMerge.py
  fi

  python3 "${runMergeFile}" \
    --input-files=file:"${outputFilePrefix}".root \
    --output-file="${outputFilePrefix}"_flattened2.root \
    --mergeNANO --isL1Scouting

  mv RunMergeCfg.py "${outputFilePrefix}"_flattened2.py

  cmsRun "${outputFilePrefix}"_flattened2.py \
    2>&1 | tee "${outputFilePrefix}"_flattened2.log
  edmFileUtil "${outputFilePrefix}"_flattened2.root
done

rm -rf __pycache__
