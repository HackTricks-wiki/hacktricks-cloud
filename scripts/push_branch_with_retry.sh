#!/usr/bin/env bash
set -euo pipefail

branch=${1:?language branch required}
max_attempts=8

for ((attempt = 1; attempt <= max_attempts; attempt++)); do
  if git push origin "HEAD:$branch"; then
    exit 0
  fi

  if ((attempt == max_attempts)); then
    echo "Failed to push $branch after $max_attempts attempts" >&2
    exit 1
  fi

  echo "Push to $branch failed (attempt $attempt/$max_attempts); refreshing the branch" >&2
  sleep $((attempt * 2))
  if git fetch origin "+refs/heads/${branch}:refs/remotes/origin/${branch}"; then
    git rebase "origin/$branch"
  fi
done
