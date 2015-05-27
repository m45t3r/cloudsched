#!/bin/bash

# Source this file before running the experiments

# http://stackoverflow.com/a/13122219
activate() {
  source "${VIRTUALENV_DIR}"/bin/activate
}

VIRTUALENV_DIR="env"
VIRTUALENV_BIN="virtualenv2"

# Fabric needs Python 2, so we need to bootstrap a Virtualenv with
# Python 2. In Arch Linux, this would be 'virtualenv2' command, that
# does not exist in Debian's based distributions.
command -v "${VIRTUALENV_BIN}" &> /dev/null || VIRTUALENV_BIN=virtualenv

if [ ! -d "${VIRTUALENV_DIR}" ]; then
  "${VIRTUALENV_BIN}" "${VIRTUALENV_DIR}"
fi

activate

pip install -r requirements.txt
