#!/bin/bash -e

jobLabel=tmp_cmsDriver

nanoFlavours=(
  L1Scout
  L1ScoutSelect
)

declare -A inputFiles=(
  ["L1Scout"]="/store/data/Run2026A/L1Scouting/L1SCOUT/v1/000/401/733/00000/81f5a1c5-a8d2-41bd-a9d8-54959c778d9f.root"
  ["L1ScoutSelect"]="/store/data/Run2026A/L1ScoutingSelection/L1SCOUT/v1/000/401/733/00000/52356b7e-e20e-4afb-bde6-6674e2b8b94f.root"
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
  edmFileUtil "${outputFilePrefix}".root
  edmDumpEventContent "${outputFilePrefix}".root | tee "${outputFilePrefix}".txt

  # Conversion from NANOEDMAOD to NANOAOD
cat <<@EOF >> "${outputFilePrefix}"_flattened.py
import FWCore.ParameterSet.Config as cms

process = cms.Process("NANOAOD")

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring("file:${outputFilePrefix}.root")
)

process.outputModule = cms.OutputModule("OrbitNanoAODOutputModule",
    fileName = cms.untracked.string("file:${outputFilePrefix}_flattened.root"),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAOD')
    ),
    compressionAlgorithm = cms.untracked.string("LZMA"),
    compressionLevel = cms.untracked.int32(9),
    outputCommands = cms.untracked.vstring(
        "drop *",
        "keep l1ScoutingRun3OrbitFlatTable_*_*_*",
        "keep uints_*_SelBx_*"
    ),
#    selectedBx = cms.InputTag("FinalBxSelector:SelBx"),
    skipEmptyBXs = cms.bool(True)
)

process.outputEndPath = cms.EndPath(process.outputModule)
@EOF
  cmsRun "${outputFilePrefix}"_flattened.py 2>&1 | tee "${outputFilePrefix}"_flattened.log
  edmFileUtil "${outputFilePrefix}"_flattened.root
done

rm -rf __pycache__
