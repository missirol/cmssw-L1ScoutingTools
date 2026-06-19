#!/bin/bash

batch_driver.py \
  -p L1ScoutSelDiJetAnalysisDriver \
  -i out1_l1sReNano/L1ScoutingSelection_*/*.root \
  -o out2_l1sSelDiJet/jobs \
  --JobFlavour espresso \
  -n 2000000
