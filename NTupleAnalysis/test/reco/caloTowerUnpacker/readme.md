Workflow implemented by Rocco Ardino to test
the unpacking and jet-clustering of CaloTowers
for L1-Scouting.

To run the test, execute
```
./testL1ScoutCaloTowerUnpacker.sh
```

**Note**: this test requires the updates introduced in
https://github.com/cms-sw/cmssw/pull/48093

The test is structured as follows.
 - Step 1:
   take one file of ZeroBias data from Run2025G in RAW format,
   and produce a NanoAOD file containing the emulated L1T CaloTowers
   (done using the "L1DPG" NanoAOD flavour).

 - Step 2:
   convert the content of the CaloTower-related branches in the NanoAOD file
   to the FEDRawData format used in the L1-Scouting system.

 - Step3:
   process with `cmsRun` the FEDRawData files produced in the previous step:
   this step unpacks the CaloTowers, and
   runs jet clustering on them using FastJet.

 - Step 4:
   validate the unpacked CaloTowers by comparing them to
   the ones stored in the NanoAOD file produced in the first step.
