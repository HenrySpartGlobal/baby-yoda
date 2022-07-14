#!/usr/bin/env bash

pkill -f launcher.py
sleep 120
nohup python3 launcher.py &