#!/bin/bash -ex

# L1Scouting
python3 Configuration/DataProcessing/test/RunPromptReco.py \
  --global-tag=160X_dataRun3_Prompt_v1 \
  --scenario=l1ScoutingEra_Run3_2026 \
  --lfn=/store/data/Commissioning2026/L1Scouting/L1SCOUT/v1/000/401/283/00000/52fd4afd-a24b-41f6-af4f-76f2b46fbfd6.root \
  --nanoaod --nanoFlavours=@L1Scout

cmsRun -e RunPromptRecoCfg.py 2>&1 | tee RunPromptReco_L1Scout.log

# L1ScoutingSelection
python3 Configuration/DataProcessing/test/RunPromptReco.py \
  --global-tag=160X_dataRun3_Prompt_v1 \
  --scenario=l1ScoutingEra_Run3_2026 \
  --lfn=/store/data/Commissioning2026/L1ScoutingSelection/L1SCOUT/v1/000/401/283/00000/2b4e19e8-8057-444d-b677-0fe7904e7379.root \
  --nanoaod --nanoFlavours=@L1ScoutSelect

cmsRun -e RunPromptRecoCfg.py 2>&1 | tee RunPromptReco_L1ScoutSelect.log
