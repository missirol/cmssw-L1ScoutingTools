#!/bin/bash -ex

THIS_DIR=$(cd $(dirname -- "${BASH_SOURCE[0]}") && pwd)

# Create grid-certificate proxy (if not already in place)
if [ ! -f "${X509_USER_PROXY}" ]; then
  voms-proxy-init --voms cms --rfc --valid 168:00
fi

###
### Neutrino_E10_gun_RunIIISummer24_PREMIX (T2_CH_CERN)
###
PILEUP_DATASET=/Neutrino_E-10_gun/RunIIISummer24PrePremix-Premixlib2024_140X_mcRun3_2024_realistic_v26-v1/PREMIX
PILEUP_DATASET_SITE=T2_CH_CERN
dasgoclient -query "file dataset=${PILEUP_DATASET} site=${PILEUP_DATASET_SITE}" \
 | sort -u > "${THIS_DIR}"/Neutrino_E10_gun_RunIIISummer24_PREMIX.txt
