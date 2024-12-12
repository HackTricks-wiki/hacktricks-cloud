#!/bin/bash

# Function to clean up a branch
do_cleanup() {
    local branch=$1
    echo "Switching to branch: $branch"

    # Check out the branch and create an orphan branch
    git fetch origin $branch
    git checkout -B $branch origin/$branch
    git branch -D temp-clean-branch 2>/dev/null
    git checkout --orphan temp-clean-branch

    # Add all files to the new orphan branch
    # rm ./path/to/file # Remove the files that are giving your problems for some weird reason
    git add .
    git commit -m "Recreating repository history for branch $branch"

    # Rename the orphan branch to the original branch name
    git branch -M temp-clean-branch $branch

    # Push the updated branch to remote
    echo "Pushing branch $branch..."
    git push --force --set-upstream origin $branch

    # Delete the temporary branch
    echo "Deleting temporary branch..."
    git branch -D temp-clean-branch
    git checkout master
}

# Get a list of all branches
branches=$(git branch -r | grep -vE 'origin/(HEAD|main|master)' | sed 's/origin\///')

# Skip the first three branches
#branches=$(echo "$branches" | tail -n +15)

echo "Detected branches (after skipping the first three):"
echo "$branches"
echo ""

# Loop through each branch
for branch in $branches; do
    echo "Do you want to clean branch $branch? (y/n)"
    read -r response

    if [[ "$response" == "y" || "$response" == "Y" ]]; then
        do_cleanup "$branch"
    else
        echo "Skipping branch $branch."
    fi

done

echo "All selected branches have been cleaned."
