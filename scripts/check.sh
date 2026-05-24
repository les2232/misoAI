#!/usr/bin/env bash
set -e

printf "status\nwhat can you do?\nvoice\ncheckin\nexcited\nfinish the Miso voice foundation\nrun the test script\nlastcheckin\nrecap\naddproject\nMiso Workboard UX\nactive\ncreated the command plan\nnone\nrun the check script\nmedium\nrenameproject\nMiso Workboard UX\nMiso Workboard UX\nrecap\nresume UX\nupdateproject\nMiso Workboard UX\nMiso Workboard UX\nactive\nadded local workboard storage\nnone\nverify scripted CLI commands\nhigh\nsnapshot\nMiso Workboard UX\nwired the workboard commands into the CLI\nupdated project recap\nnone\nrun scripts/check.sh\nlastsnapshot\nhandoff UX\nclose\n" | python3 main.py
python3 -m compileall miso_core main.py
