#!/bin/bash -ex

if [ $# -ne 3 ]; then
  set +x
  printf "\n"
  printf "%s\n" ">>> ERROR - invalid command-line arguments (must be exactly 3 strings)."
  printf "%s\n" "            [1] Path to input directory."
  printf "%s\n" "            [2] Label of the data set (name of the input subdirectory)."
  printf "%s\n" "            [3] Path to output directory."
  printf "\n"
  exit 1
fi

inpdir="${1}"
datasetLabel="${2}"
outdir="${3}"

mkdir -p "${outdir}"

for nnn in {0..4}; do
  outFile="${outdir}"/"${datasetLabel}"_"${nnn}".root

  if [ -f "${outFile}" ]; then
    printf "%s\n" "ERROR - target output file already exists: ${outFile}"
    exit 1
  fi

#  haddnano.py "${outFile}" "${inpdir}"/"${datasetLabel}"/job_"${nnn}"*/*root
#  rm -rf "${inpdir}"/"${datasetLabel}"/job_"${nnn}"*/

  haddnano.py "${outFile}" "${inpdir}"/"${datasetLabel}"/out_"${nnn}"*.root
  rm -f "${inpdir}"/"${datasetLabel}"/out_"${nnn}"*.root
done
unset nnn

outFile="${outdir}"/"${datasetLabel}".root

if [ -f "${outFile}" ]; then
  printf "%s\n" "ERROR - target output file already exists: ${outFile}"
  exit 1
fi

haddnano.py "${outFile}" "${outdir}"/"${datasetLabel}"_*.root

rm -f "${outdir}"/"${datasetLabel}"_*.root
