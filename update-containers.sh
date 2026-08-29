#!/bin/bash

CTS=(100 103 104)

for CT in "${CTS[@]}"; do
    (
        echo "===== CT ${CT}: START ====="

        if ! pct status "$CT" 2>/dev/null | grep -q '^status: running$'; then
            echo "===== CT ${CT}: SKIP (not running) ====="
            exit 1
        fi

        pct exec "$CT" -- sh -c 'apk update && apk upgrade'
        RC=$?

        if [ "$RC" -eq 0 ]; then
            echo "===== CT ${CT}: SUCCESS ====="
        else
            echo "===== CT ${CT}: FAILED (rc=${RC}) ====="
        fi

        exit "$RC"
    ) &
done

wait
