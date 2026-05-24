#!/usr/bin/env bash
set -e

printf "status\nexit\n" | python3 main.py
python3 -m compileall miso_core main.py
