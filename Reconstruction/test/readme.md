Configurations to test the processing of L1-Scouting data
=========================================================

 - *l1sRepackSRD_cfg.py*:
    config to convert files in Scouting Raw Data (SRD) format
    into one EDM file containing the raw data from the L1-Scouting FEDs.

 - *l1sReco_cfg.py*:
    config to run the main L1-Scouting modules on EDM files containing
    raw data from the L1-Scouting FEDs (SDSRawDataCollection).

Example.
```
rm -rf tmp

cmsRun l1sRepackSRD_cfg.py \
  -i /eos/user/m/missirol/l1s_data_250219/run000001 \
  -o /eos/user/m/missirol/l1s_data_250219_repacked.root \
  --baseDir tmp \
  -n -1 -l 770 --report 1000

rm -rf tmp

cmsRun l1sReco_cfg.py \
  -i /eos/user/m/missirol/l1s_data_250219_repacked.root \
  -o tmp.root \
  -n 1 -e 1:770:201588736
```
