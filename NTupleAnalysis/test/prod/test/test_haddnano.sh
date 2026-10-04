#!/bin/bash -ex

[ $# -eq 1 ] || exit 1

cd "${1}"

for sampleName in $(ls -d *); do
  haddnano.py "${sampleName}".root "${sampleName}"/job*/*.root
  rm -rf "${sampleName}"
done
