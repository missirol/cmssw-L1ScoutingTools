#!/bin/bash -ex

[ $# -eq 1 ] || exit 1

TARGET_DIR="${1}"

merge_batchOutputs.py \
  -i "${TARGET_DIR}"/jobs/*.root \
  -o "${TARGET_DIR}"/outputs

jetMETPerformance_harvester.py \
  -i "${TARGET_DIR}"/outputs/*.root \
  -o "${TARGET_DIR}"/harvesting \
  --profile-mean-stats-per-bin 10
