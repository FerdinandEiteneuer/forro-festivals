#!/bin/bash


echo "Test task starting"

pwd

CURRENT_DATE=$(date +"%Y-%m-%d_%H-%M-%S")

TEST_FILE=$HOME/test_file_$CURRENT_DATE.txt

echo "This is a test file" > $TEST_FILE
echo `date` >> $TEST_FILE
