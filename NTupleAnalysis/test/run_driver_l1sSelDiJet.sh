#!/bin/bash

batch_driver.py \
  -p L1ScoutSelDiJetAnalysisDriver \
  -i "${CMSSW_BASE}"/src/L1ScoutingTools/NanoAOD/test/tmpout2/L1ScoutingSelection_Run2026D/*.root \
  -o out2_l1sSelDiJet/jobs \
  --JobFlavour espresso \
  -n 1000000
