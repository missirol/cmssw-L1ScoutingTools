#!/bin/bash

if [ ! -z ${L1SADIR} ]; then
  echo "environment already set: L1SADIR=${L1SADIR}"
  return
fi

export L1SADIR=${PWD}

l1s_clang_format() {
  clang-format -i --style file:"${CMSSW_BASE}"/src/.clang-format "${CMSSW_BASE}"/src/L1ScoutingTools/*/*/*.{h,cc}
}

export PATH=${L1SADIR}:${PATH}

export PYTHON3PATH=${PWD}:${PWD}/common:${PYTHON3PATH}
export PYTHONDONTWRITEBYTECODE=1
