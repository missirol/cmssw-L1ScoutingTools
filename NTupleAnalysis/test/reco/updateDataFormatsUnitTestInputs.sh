#!/bin/bash

cmsswRelease=CMSSW_16_1_0_pre3
branchName=devel_l1sDataFormatsUnitTest_1610pre3

rm -rf "${branchName}"
mkdir -p "${branchName}"
cd "${branchName}"

cmsrel "${cmsswRelease}"
cd "${cmsswRelease}"/src
cmsenv

git cms-init --ssh
git checkout -b "${branchName}"
git cms-addpkg DataFormats/L1Scouting
git clone git@github.com:"${USER}"/DataFormats-L1Scouting.git DataFormats/L1Scouting/data -o "${USER}"
git cms-checkdeps -bpha

scram b

for splitLevel in 0 99; do
  cmsRun DataFormats/L1Scouting/test/create_L1Scouting_test_file_cfg.py \
    -o DataFormats/L1Scouting/data/testL1Scouting_v3_v3_v3_v3_v3_v3_v3_v3_"${CMSSW_VERSION:6}"_split_"${splitLevel}".root \
    -s "${splitLevel}"
done
unset splitLevel

cd DataFormats/L1Scouting/data
git add testL1Scouting_v3_v3_v3_v3_v3_v3_v3_v3_"${CMSSW_VERSION:6}"_split_*.root
git checkout -b "${branchName}"
git commit \
  -m 'Unit-test input files produced with CMSSW_16_1_0_pre3' \
  -m 'These files include products using v3 of the data formats l1ScoutingRun3::CaloTower (cms-sw/cmssw#48093) and l1ScoutingRun3::CaloJet (cms-sw/cmssw#50304).'
git push "${USER}" "${branchName}" -f

cd ../../..

git cherry-pick 47b7aaf5968
git push my-cmssw devel_l1sDataFormatsUnitTest_1610pre3 -f

scram b runtests
