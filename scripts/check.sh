#!/usr/bin/env bash
set -e

printf "status\nwhat can you help me do?\nask help me focus\nremember mood excited\nwhat do you remember?\nrecall mood\nmemories\nforget mood\nclose\n" | python3 main.py
python3 -m compileall miso_core main.py
