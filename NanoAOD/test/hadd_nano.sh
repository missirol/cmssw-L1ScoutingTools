#!/bin/bash -ex

inpdir=output_l1sNTuple_260221
sampleName=Run3Winter25_QCD_PtFlat15to7000_13p6TeV_FlatPU0to120

for nnn in {0..4}; do
  haddnano.py \
    "${inpdir}"/"${sampleName}"_"${nnn}".root \
    "${inpdir}"/"${sampleName}"/job_"${nnn}"*/*root

  rm -rf "${inpdir}"/"${sampleName}"/job_"${nnn}"*/
done
unset nnn

haddnano.py \
  "${inpdir}"/"${sampleName}".root \
  "${inpdir}"/"${sampleName}"_*.root

rm -f "${inpdir}"/"${sampleName}"_*.root
