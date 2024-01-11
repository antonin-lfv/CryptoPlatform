#!/bin/bash

# File to delete
FILE="db.sqlite"

# Verify if the file exists
if [ -f "$FILE" ]; then
    rm "$FILE"
    echo "File deleted."
else
    echo "Error: File $FILE does not exist."
fi
