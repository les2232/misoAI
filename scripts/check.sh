#!/usr/bin/env bash
set -e

printf "status\nremember mood excited\nrecall mood\nmemories\nforget mood\nexit\n" | python3 main.py
python3 -m compileall miso_core main.py
