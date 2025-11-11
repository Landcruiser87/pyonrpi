#!/usr/bin/env bash

# # 1. Calculate a random delay between 0 and 1799 seconds (30 minutes)
# RANDOM_DELAY=$(( $RANDOM % 1800 ))

# # 2. Pause execution for the delay 
# sleep $RANDOM_DELAY

# 3. Define the project directory
# Using the HOME variable ensures this works regardless of how cron is run.
GIT_PATH="/usr/bin/git"
POETRY_PATH="$HOME/.local/bin/poetry"
PROJECT_DIR="$HOME/gitrepos/pyonrpi"
VENV_PATH="$PROJECT_DIR/.venv"
USER="andy"
COMMIT_MESSAGE="Auto update for $USER on $(date +'%Y-%m-%d %H:%M:%S')"
PYTHON_INTERPRETER="$VENV_PATH/bin/python"

# 4. Change directory and run the Python script
cd "$PROJECT_DIR" || { echo "Error: Failed to change directory to $PROJECT_DIR" >&2; exit 1; }

#Git Pull to update codebase
echo "--- Performing Git Pull ---"
"$GIT_PATH" pull origin main || { echo "Error: Git pull failed." >&2; exit 1; }

#Take naps to give time for git to update
sleep 2

#Run the Python Script
echo "--- Running main.py ---"

"$POETRY_PATH" run "$PYTHON_INTERPRETER" scripts/main.py $USER || { echo "Error: Python script failed." >&2; exit 1; }

#Git Commit & Push: Save and send changes to GitHub. Check if the script created any changes to commit (Modified, New, or Deleted) git status --porcelain returns lines for all changed/untracked files.
if [[ -n $("$GIT_PATH" status --porcelain) ]]; then
    echo "--- Changes detected. Committing changes ---"
    
    # Stage all changes (new, modified, and deleted files) The -A flag stages everything: new files, modifications, and deletions.
    "$GIT_PATH" add -A .
    
    # Commit the changes
    "$GIT_PATH" commit -m "$COMMIT_MESSAGE"
    
    # Push the changes to the remote repository
    echo "--- Pushing to GitHub ---"
    "$GIT_PATH" push -u origin main || { echo "Error: Git push failed." >&2; exit 1; }
else
    echo "--- No changes detected. Skipping commit/push. ---"
fi

#Exit Bash file
exit 0