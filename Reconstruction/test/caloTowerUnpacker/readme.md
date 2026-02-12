Workflow implemented by Rocco Ardino
to test the unpacking and jet-clustering of CaloTowers for L1-Scouting.

To run the test, execute
```
./testL1ScoutCaloTowerUnpacker.sh
```

**Note**: this test depends on the updates introduced in
https://github.com/cms-sw/cmssw/pull/48093

The test is structured as follows.
 - Take one file of ZeroBias data from Run2025G in RAW format,
   and produce a NanoAOD containing the emulated L1T CaloTowers
   ("L1DPG" NanoAOD flavour).
 - Convert the content of the CaloTower-related branches in the NanoAOD file
   to the FEDRawData format used in the L1-Scouting system.
 - Process the FEDRawData files from the previous step:
   this step unpacks the CaloTowers, and
   runs jet clustering on them using FastJet.
