#!/bin/bash

set -e

cd "$(dirname "$0")"

python "./build.py" --mode fast "$@"
