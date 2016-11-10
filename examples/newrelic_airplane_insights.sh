#!/bin/sh

while true; do
    nohup python ./newrelic_airplane_insights.py >> newrelic_airplane_insights.log 2>&1
    echo "'newrelic_airplane_insights' crashed with exit code $?. Respawning..."
    sleep 1
done &
