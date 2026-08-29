#!/bin/bash

batch_driver.py \
  -p L1ScoutSelDiJetAnalysisDriver \
  -i out1_l1sReNano/L1ScoutingSelection_*/*_run403937_ls0525_part1.root \
  -o out2_l1sSelDiJet/jobs \
  --JobFlavour espresso \
  -n 1000000
