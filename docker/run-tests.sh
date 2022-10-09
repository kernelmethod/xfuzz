#!/bin/bash

set -euo pipefail

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

    set -x
    docker compose ${COMPOSE_FILES} \
        run --rm -i \
        -v "${CODE_DIRECTORY}":/opt/xfuzz/xfuzz:ro \
        xfuzz-client /usr/local/bin/run-tests.sh
}

usage() {
    cat << EOF >&2
Usage: ./$(basename $0) /path/to/xfuzz/code

EOF

    exit ${1:-1}
}

if [ ! $# -eq 1 ]; then
    usage
fi

USE_APPARMOR="${XFUZZ_USE_APPARMOR:-1}"
main "$1"
