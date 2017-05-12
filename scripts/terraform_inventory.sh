#!/usr/bin/env bash

set -euo nounset -o pipefail                      # Treat unset variables as an error
INVENTORY_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ati "$@" --root $INVENTORY_DIR
