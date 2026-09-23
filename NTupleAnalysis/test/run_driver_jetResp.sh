#!/bin/bash

batch_driver.py \
  -i out1/*/*.root \
  -o out2_jetResp/jobs \
  --JobFlavour microcentury \
  -n 50000 \
  -p JetResponseAnalysisDriver
