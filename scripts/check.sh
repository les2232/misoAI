#!/usr/bin/env bash
set -e

printf "status\nask who are you\nask what can you do\nask help me focus\nremember mood excited\nask what do you remember\nrecall mood\nmemories\nforget mood\nexit\n" | python3 main.py
python3 -m compileall miso_core main.py
