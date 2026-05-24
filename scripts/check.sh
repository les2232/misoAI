#!/usr/bin/env bash
set -e

python3 main.py
python3 -m compileall miso_core main.py
