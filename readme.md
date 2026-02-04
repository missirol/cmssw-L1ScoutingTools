cmssw-L1ScoutingTools
=====================

Extra CMSSW packages related to Level-1 Scouting.

## Setup

Minimal setup instructions.
```bash
cmsrel CMSSW_15_0_17
cd CMSSW_15_0_17/src
cmsenv
git cms-init --ssh
git cms-merge-topic missirol:devel_l1sTools3
git clone git@github.com:missirol/cmssw-L1ScoutingTools.git L1ScoutingTools -o missirol
scram build
```
