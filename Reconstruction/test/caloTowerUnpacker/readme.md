Workflow implemented by Rocco Ardino
to test the unpacking and jet-clustering of CaloTowers for L1-Scouting.

To run the test, execute
```
./testL1ScoutCaloTowerUnpacker.sh
```

The test is structured as follows.
 - Take one file of ZeroBias data from Run2025G in RAW format,
   and produce a NanoAOD containing the emulated L1T CaloTowers
   ("L1DPG" NanoAOD flavour).
 - Convert the content of the CaloTower-related branches in the NanoAOD file
   to the FEDRawData format used in the L1-Scouting system.
 - Process the FEDRawData files from the previous step,
   running the CaloTower unpacker and clustering the CaloTowers into jets.
