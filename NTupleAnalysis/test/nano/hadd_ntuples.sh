#!/bin/bash -ex

if [ $# -ne 1 ]; then
  set +x
  printf "\n"
  printf "%s\n" ">>> ERROR - invalid command-line arguments (must be exactly 3 strings)."
  printf "%s\n" "            [1] Path to input directory."
  printf "\n"
  exit 1
fi

inpdir="${1}"
datasetLabel="${2}"
outdir="${inpdir}"

mkdir -p "${outdir}"

datasetLabels=($(ls -1 "${inpdir}"))

for datasetLabel in "${datasetLabels[@]}"; do
  inpdir2="${outdir}"/"${datasetLabel}"

  if [ ! -d "${inpdir2}" ]; then
    continue
  fi

  outFile="${inpdir2}".root

  if [ -f "${outFile}" ]; then
    printf "%s\n" "ERROR - target output file already exists: ${outFile}"
    exit 1
  fi

  for nnn in {0..9}; do
    outFile2="${inpdir2}"_"${nnn}".root

    if [ -f "${outFile2}" ]; then
      printf "%s\n" "ERROR - target output file already exists: ${outFile}"
      exit 1
    fi

    inpPrefix="${inpdir}"/"${datasetLabel}"/out_"${nnn}"

    if [ $(ls "${inpPrefix}"*.root 2> /dev/null | wc -l) -gt 0 ]; then
      haddnano.py "${outFile2}" "${inpPrefix}"*.root
      rm -rf "${inpPrefix}"*.root
    fi

#    haddnano.py "${outFile2}" "${inpPrefix}"*.root
#    rm -f "${inpPrefix}"*.root
  done
  unset nnn

  haddnano.py "${outFile}" "${inpdir2}"_*.root

  rm -rf "${inpdir2}"/ "${inpdir2}"_*.root
done
