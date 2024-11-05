#!/bin/bash

# Path to your Python script and Python environment
PYTHON_SCRIPT="/Users/riyaaggarwal/Desktop/293/instagram_threads_scraper/parse_1min.py"
PYTHON_PATH="/Users/riyaaggarwal/Desktop/bin/python3"  # Path to Python in your environment
LOG_FILE="/Users/riyaaggarwal/Desktop/293/instagram_threads_scraper/logs/cron_log.txt"

# Infinite loop to run the script every 20 minutes
while true; do
    # Print start message with timestamp
    echo "[$(date)] Starting Python script execution" >> $LOG_FILE 2>&1
    
    # Run the Python script and append its output and errors to the log file
    $PYTHON_PATH $PYTHON_SCRIPT >> $LOG_FILE 2>&1
    
    # Print completion message with timestamp
    echo "[$(date)] Python script execution completed" >> $LOG_FILE 2>&1
    
    # Sleep for 20 minutes (1200 seconds)
    echo "sleep start"
    sleep 10m
    echo "sleep donee"
done

