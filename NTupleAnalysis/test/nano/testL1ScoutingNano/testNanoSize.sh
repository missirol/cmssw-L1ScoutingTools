#!/bin/bash -e

jobLabel=tmp2_cmsDriver

nanoFlavours=(
  L1Scout
#  L1ScoutSelect
)

declare -A inputFiles=(
  ["L1Scout"]="file:/eos/cms/tier0/store/backfill/1/data/Tier0_REPLAY_2026/L1Scouting/L1SCOUT/v29144434/000/402/472/00000/2fbec517-e7ca-4bfc-bba9-4fb3ddb97077.root"
  ["L1ScoutSelect"]="/store/data/Run2026B/L1ScoutingSelection/L1SCOUT/v1/000/402/144/00000/56a86b0d-c4a0-4ffc-84c5-158494ec8ecc.root"
)

maxEvents=300

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
done

rm -rf __pycache__
