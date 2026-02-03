#!/bin/bash

batch_driver.py \
  -i out1/*root \
  -o out2_jetPerf/jobs \
  -n 50000 \
  --opt jecA_filePath=/eos/cms/store/cmst3/group/daql1scout/run3_calotowers/jet_pt_corrections/mc_qcd_2025/graph_SC.root \
  -p JetMETPerformanceAnalysisDriver
