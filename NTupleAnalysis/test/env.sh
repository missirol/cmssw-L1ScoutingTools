#!/bin/bash

if [ ! -z ${L1SADIR} ]; then
  echo "environment already set: L1SADIR=${L1SADIR}"
  return
fi

export L1SADIR=${PWD}

export PATH=${L1SADIR}:${PATH}

export PYTHON3PATH=${PWD}:${PWD}/common:${PYTHON3PATH}
export PYTHONDONTWRITEBYTECODE=1
