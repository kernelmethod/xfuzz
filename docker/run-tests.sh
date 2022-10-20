#!/bin/bash

set -euo pipefail

DEFAULT_USE_APPARMOR=0
DEFAULT_COMMAND="/usr/local/bin/run-tests.sh"

main() {
    CODE_DIRECTORY=$(readlink -m "$1")

    if [ ! -d "${CODE_DIRECTORY}" ]; then
        printf "Error: input path ${CODE_DIRECTORY} does not point to a directory\n\n" >&2
        usage
    fi

    COMPOSE_FILES="-f docker-compose.yml"
    if [ "${USE_APPARMOR}" -eq 1 ]; then
        COMPOSE_FILES="${COMPOSE_FILES} -f overrides/apparmor.yml"
    fi

    # We temporarily copy the files in $CODE_DIRECTORY to a temporary directory
    XFUZZ_TMP=$(mktemp -d)
    echo "Temporarily copying files to $XFUZZ_TMP..."
    cp -r --no-preserve=mode,ownership "${CODE_DIRECTORY}" "${XFUZZ_TMP}/xfuzz"
    chmod -R go+rx "${XFUZZ_TMP}/xfuzz"
    echo ""

    set -x
    ls -la "${XFUZZ_TMP}/xfuzz"
    docker compose ${COMPOSE_FILES} \
        run --rm -i \
        -v "${XFUZZ_TMP}/xfuzz":/opt/xfuzz/xfuzz:ro \
        xfuzz-client $(echo "${COMMAND}") \
        || true
    set +x

    echo "Cleaning up ${XFUZZ_TMP}..."
    rm -rf "${XFUZZ_TMP}"
}

usage() {
    cat << EOF >&2
Usage: ./$(basename $0) /path/to/xfuzz/code

Environment variables:

    XFUZZ_USE_APPARMOR
        Specifies whether or not the custom AppArmor profile specified in xfuzz.profile
        should be used. This parameter should be set to 0 or 1 (defaults to ${DEFAULT_USE_APPARMOR}).

    XFUZZ_COMMAND
        The command to run in the Docker container run by the script. It may be useful
        to override this for debugging purposes. Defaults to ${DEFAULT_COMMAND}
EOF

    exit ${1:-1}
}

if [ ! $# -eq 1 ]; then
    usage
fi

USE_APPARMOR="${XFUZZ_USE_APPARMOR:-${DEFAULT_USE_APPARMOR}}"
COMMAND="${XFUZZ_COMMAND:-${DEFAULT_COMMAND}}"
main "$1"
