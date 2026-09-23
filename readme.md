cmssw-L1ScoutingTools
=====================

This repository contains extra CMSSW subpackages
to create and analyze NanoAOD data sets for MC samples and
collisions data collected by CMS in 2026 with the Level-1 Scouting (L1S) system.

The tools in this package currently require using the
following custom branch of the [cms-sw/cmssw](https://github.com/cms-sw/cmssw) package:
https://github.com/missirol/cmssw/commits/devel_l1sRun3CaloTowers_170X

The latter branch is based on `CMSSW_17_0_X`,
and it contains the definition of custom NanoAOD flavors
containing L1T and/or L1S collections.
These flavours mainly differ in the type of input data they can handle,
be that MC samples, standard primary data sets, or L1S data sets.

The tools in this repository are tailored towards a single use case,
i.e. the analysis of L1S CaloLayer-1 data (CaloTowers) collected in 2026.

The rest of this document details how
to set up the software in this package,
the purpose of some of its main scripts,
as well as recipes to produce different
types of NanoAOD data sets for L1S analyses.

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



## NTuple production

Example of how to produce a set of ntuples (flat NanoAOD)
for MC samples and 2026 L1-Scouting data.

The specifics of the input data (name of the data sets,
the amounts of statistics, batch-job parameters, etc)
are currently hard-coded in the bash scripts used below.
The names of the output directories are just examples;
the first one (`OUTDIR1`) is used as local directory to host log files and
manage the monitoring of the batch job (incl. their resubmission, if needed);
the second directory (`OUTDIR2`) contains the outputs of the batch jobs, so
one must ensure that there is sufficient disk space available in that directory.
None of the scripts make any assumptions on the values of `OUTDIR1` and `OUTDIR2`.

```bash
cd "${CMSSW_BASE}"/src/L1ScoutingTools/NTupleAnalysis/test/nano

OUTDIR1=260914
OUTDIR2=/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/"${USER}"/l1scout/ntuples/"${OUTDIR1}"

# MC samples (campaign: Run3Winter25)
./run_l1sNTuple_MC_Run3Winter25.sh "${OUTDIR1}" "${OUTDIR2}"

# Data (2026 pp collisions)
./run_l1sNTuple_Data_2026.sh "${OUTDIR1}" "${OUTDIR2}"

# Monitor status of batch jobs on HTCondor;
# adding "-r" enables the (re)submission of jobs
bmonitor -i "${OUTDIR1}" -r

# Once all the jobs are completed, merge their outputs
./hadd_ntuples.sh "${OUTDIR2}"
```
