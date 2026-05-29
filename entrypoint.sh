#!/bin/bash

if [ "$LUMON_ROLE" = "LEAD" ]; then
    echo "CLEARANCE LEVEL: LEAD. Administrative bridge active."
    sleep infinity
else
    echo "===================================================="
    echo "   MDR WORKSTATION PROVISIONED SUCCESSFULLY          "
    echo "   Awaiting console connection...                    "
    echo "===================================================="
    sleep infinity
fi
