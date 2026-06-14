#!/bin/bash -e

jobLabel=tmp_testL1ScoutingReReco

nanoFlavours=(
  L1ScoutReReco
  L1ScoutReRecoSelect
)

declare -A inputFiles=(
  ["L1ScoutReReco"]="/store/data/Run2026B/L1Scouting/L1SCOUT/v1/000/402/244/00001/65ecfc3f-65b1-443b-bf0a-a087d35dc453.root"
  ["L1ScoutReRecoSelect"]="/store/data/Run2026D/L1ScoutingSelection/L1SCOUT/v1/000/403/937/00000/d5af5899-290d-44b7-b33d-e77a487e3fb2.root"
)

maxEvents=100

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
    --nThreads 8 \
    -s NANO:@"${nanoFlavour}"
  edmConfigDump --prune "${outputFilePrefix}".py > "${outputFilePrefix}"_dump.py
  edmFileUtil "${outputFilePrefix}".root
done

rm -rf __pycache__
