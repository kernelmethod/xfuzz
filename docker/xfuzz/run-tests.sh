#!/bin/bash

set -euo pipefail

PAUSE_TIME=1
SPEED_TEST_TIMEOUT=120

# Run unit tests with pytest

if [ ! -d ./xfuzz ]; then
    echo "./xfuzz directory not found. Did you mount it correctly?"
    exit 1
fi

printf "Running unit tests\n\n\n"
sleep "${PAUSE_TIME}"

set -x
pytest || true
set +x

printf "\n\n\n"
echo "------------------------------------------------------------"
printf "Running speed tests\n\n\n"
sleep "${PAUSE_TIME}"

set -x

time \
timeout "${SPEED_TEST_TIMEOUT}" \
python3 -m xfuzz -w 'test/wordlists/common.txt' \
    -H 'Content-Type: application/json' \
    -X POST \
    -mc 200 \
    -d '{"username": "admin", "password": "FUZZ"}' \
    -u http://proxy.xfuzz.lab/auth/login

set +x
