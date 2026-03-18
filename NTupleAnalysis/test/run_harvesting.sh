#!/bin/bash -ex

[ $# -eq 1 ] || exit 1

TARGET_DIR="${1}"

# Merge outputs of batch jobs into one file per sample
merge_batchOutputs.py \
  -i "${TARGET_DIR}"/jobs/*.root \
  -o "${TARGET_DIR}"/outputs

# Harvesting step on the outputs of the previous step
# (adds profiles and efficiencies, in a somewhat ad-hoc way)
for harvInputFile in $(ls -1 "${TARGET_DIR}"/outputs/*.root); do
  jetMETPerformance_harvester.py \
    -i "${harvInputFile}" \
    -o "${TARGET_DIR}"/harvesting \
    --profile-mean-stats-per-bin 10
done
