#!/bin/bash
# Script to run the scraper within a screen

VAL=$(ps aux | grep 'WSB' | awk '$11 != "grep" {print}' | wc -l)

if [ $VAL -eq 0 ]
then
    screen python3 WSB_Scraper.py
else
    echo "Could not start WSB_Scraper (Already running)"
fi
