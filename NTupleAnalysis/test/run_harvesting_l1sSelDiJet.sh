#!/bin/bash -ex

[ $# -eq 1 ] || exit 1

TARGET_DIR="${1}"

# Merge outputs of batch jobs into one file per sample
merge_batchOutputs.py \
  -i "${TARGET_DIR}"/jobs/*.root \
  -o "${TARGET_DIR}"/outputs \
  -m "^(.*)_run[0-9]+_ls[0-9]+(|_part[0-9]+)__[0-9]+$"
