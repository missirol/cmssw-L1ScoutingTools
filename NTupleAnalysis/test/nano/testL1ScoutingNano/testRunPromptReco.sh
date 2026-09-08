#!/bin/bash -ex

#INPUTFILE_L1SCOUT1=/store/data/Commissioning2026/L1Scouting/L1SCOUT/v1/000/401/283/00000/52fd4afd-a24b-41f6-af4f-76f2b46fbfd6.root
#INPUTFILE_L1SCOUT2=/store/data/Commissioning2026/L1ScoutingSelection/L1SCOUT/v1/000/401/283/00000/2b4e19e8-8057-444d-b677-0fe7904e7379.root

INPUTFILE_L1SCOUT1=file:tmp_l1Scout_output_hltOutputL1Scouting.root
INPUTFILE_L1SCOUT2=file:tmp_l1Scout_output_hltOutputL1ScoutingSelection.root

runPromptReco="${CMSSW_BASE}"/src/Configuration/DataProcessing/test/RunPromptReco.py

if [ ! -f "${runPromptReco}" ]; then
  runPromptReco="${CMSSW_RELEASE_BASE}"/src/Configuration/DataProcessing/test/RunPromptReco.py
fi

# L1Scouting
python3 "${runPromptReco}" \
  --global-tag=160X_dataRun3_Prompt_v1 \
  --scenario=l1ScoutingEra_Run3_2026 \
  --lfn="${INPUTFILE_L1SCOUT1}" \
  --nanoaod --nanoFlavours=@L1Scout

edmConfigDump RunPromptRecoCfg.py > RunPromptReco_L1Scout.py
cmsRun RunPromptReco_L1Scout.py 2>&1 | tee RunPromptReco_L1Scout.log
mv output.root RunPromptReco_L1Scout.root

# L1ScoutingSelection
python3 "${runPromptReco}" \
  --global-tag=160X_dataRun3_Prompt_v1 \
  --scenario=l1ScoutingEra_Run3_2026 \
  --lfn="${INPUTFILE_L1SCOUT2}" \
  --nanoaod --nanoFlavours=@L1ScoutSelect

edmConfigDump RunPromptRecoCfg.py > RunPromptReco_L1ScoutSelect.py
cmsRun RunPromptReco_L1ScoutSelect.py 2>&1 | tee RunPromptReco_L1ScoutSelect.log
mv output.root RunPromptReco_L1ScoutSelect.root
