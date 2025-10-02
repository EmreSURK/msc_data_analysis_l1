#!/bin/bash

# Parametre kontrolü
if [ $# -eq 0 ]; then
    echo "Please add a commit message"
    exit 1
fi

# Parametreyi al
COMMIT_MSG="$1"

git add .
git commit -m "$COMMIT_MSG"
git push origin master