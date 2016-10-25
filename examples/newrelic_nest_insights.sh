#!/bin/sh

while true; do
    sudo nohup python ./newrelic_nest_insights.py >> newrelic_nest_insights.log 2>&1
    echo "'newrelic_nest_insights' crashed with exit code $?. Respawning..."
    sleep 1
done &
