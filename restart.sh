#!/usr/bin/env bash

echo "Stopping Bot...."
pkill -f launcher.py
sleep 10
echo "Restarting Bot...."
nohup python3 launcher.py &