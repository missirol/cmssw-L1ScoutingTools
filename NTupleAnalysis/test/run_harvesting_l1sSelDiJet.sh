#!/bin/bash -e

TARGET_DIR=out2_l1sSelDiJet_sel0
[ $# -eq 0 ] || TARGET_DIR="${1}"

# Merge outputs of batch jobs into one file per sample
merge_batchOutputs.py \
  -i "${TARGET_DIR}"/jobs/*/job_*/out.root \
  -o "${TARGET_DIR}"/outputs \
  -m "^(.*)/jobs/(.*)/job_[0-9]+/out.root$" -x 2
