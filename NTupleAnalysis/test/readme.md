### Tools for Jet/MET Analysis

Workflow to produce Jet/MET performance plots from "flat" ROOT NTuples.

#### Setup

* Update global environment variables:
```
source env.sh
```

#### Prepare Analysis NTuples from batch/crab3 outputs

* Create output directory with one .root for each crab3 task:
```
hadd_ntuples.py -i input_dirs -o out1 -s DQM -l 0
```

#### Submit Analysis Jobs to Batch System (HT-Condor)

* Create scripts for submission of batch jobs:
```
batch_driver.py -i out1/*root -o out2/jobs -n 50000 --opt jecA_filePath=/eos/cms/store/cmst3/group/daql1scout/run3_calotowers/jet_pt_corrections/mc_qcd_2025/graph_SC.root -p JetMETPerformanceAnalysisDriver -l 0
```

* Monitoring and (re)submission of batch jobs:
```
batch_monitor.py -i out2
```

#### Harvesting of Outputs

* Merge outputs of batch jobs:
```
merge_batchOutputs.py -i out2/jobs/*.root -o out2/outputs -l 0
```

* Harvest outputs (manipulates histograms, produces profiles, efficiencies, etc):
```
jetMETPerformance_harvester.py -i out2/outputs/*.root -o out2/harvesting --profile-mean-stats-per-bin 10 -l 0
```
