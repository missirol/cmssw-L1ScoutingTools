cmssw-L1ScoutingTools
=====================

Extra CMSSW packages related to Level-1 Scouting.

## Setup

Minimal setup instructions.
```bash
cmsrel CMSSW_17_0_0_pre5
cd CMSSW_17_0_0_pre5/src
cmsenv
git cms-init --ssh
git cms-merge-topic missirol:devel_l1sRun3CaloTowers_170X
git clone git@github.com:missirol/cmssw-L1ScoutingTools.git L1ScoutingTools -o missirol
scram build
```
