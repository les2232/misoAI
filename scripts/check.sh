#!/usr/bin/env bash
set -e

printf "status\nwhat can you do?\ncheckin\nexcited\nfinish the Miso check-in feature\nrun the test script\nlastcheckin\nclose\n" | python3 main.py
python3 -m compileall miso_core main.py
