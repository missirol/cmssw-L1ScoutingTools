#!/bin/bash -e

jobLabel=tmp_cmsDriver2

nanoFlavours=(
  L1ScoutReReco
  L1ScoutReRecoSelect
)

declare -A inputFiles=(
  ["L1ScoutReReco"]="/store/data/Run2026B/L1Scouting/L1SCOUT/v1/000/402/244/00001/65ecfc3f-65b1-443b-bf0a-a087d35dc453.root"
  ["L1ScoutReRecoSelect"]="/store/data/Run2026B/L1ScoutingSelection/L1SCOUT/v1/000/402/244/00001/02fbf04e-ccaa-497b-94c1-08a0834f905d.root"
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
done

rm -rf __pycache__
