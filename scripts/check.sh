#!/usr/bin/env bash
set -e

printf "status\nwhat can you do?\nvoice\ncheckin\nexcited\nfinish the Miso voice foundation\nrun the test script\nlastcheckin\nclose\n" | python3 main.py
python3 -m compileall miso_core main.py
