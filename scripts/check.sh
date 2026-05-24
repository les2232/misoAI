#!/usr/bin/env bash
set -e

printf "status\nwhat can you do?\nvoice\ncheckin\nexcited\nfinish the Miso voice foundation\nrun the test script\nlastcheckin\nrecap\naddproject\nMiso Workboard\nactive\ncreated the command plan\nnone\nrun the check script\nmedium\nrecap\nresume Miso Workboard\nupdateproject\nMiso Workboard\nMiso Workboard\nactive\nadded local workboard storage\nnone\nverify scripted CLI commands\nhigh\nsnapshot\nMiso Workboard\nwired the workboard commands into the CLI\nupdated project recap\nnone\nrun scripts/check.sh\nlastsnapshot\nhandoff Miso Workboard\nclose\n" | python3 main.py
python3 -m compileall miso_core main.py
