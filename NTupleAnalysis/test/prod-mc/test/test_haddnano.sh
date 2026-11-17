#!/bin/bash -ex

[ $# -eq 1 ] || exit 1

cd "${1}"

for sampleName in $(ls -d *); do
  cd "${sampleName}"
  haddnano.py ../"${sampleName}".root job_*/NANO.root
  cd "${OLDPWD}"
  rm -rf "${sampleName}"
done
