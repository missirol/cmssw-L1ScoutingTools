#!/bin/bash

batch_driver.py \
  -i out1/*/*{QCD,TT}*.root \
  -o out2_jetPerf/jobs \
  --JobFlavour microcentury \
  -n 50000 \
  -p JetPerformanceAnalysisDriver
