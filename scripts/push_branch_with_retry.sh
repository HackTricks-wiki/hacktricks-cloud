#!/usr/bin/env bash
set -euo pipefail

branch=${1:?language branch required}
max_attempts=8

for ((attempt = 1; attempt <= max_attempts; attempt++)); do
  if git push --set-upstream origin "HEAD:refs/heads/$branch"; then
    exit 0
  fi

  if ((attempt == max_attempts)); then
    echo "Failed to push $branch after $max_attempts attempts" >&2
    exit 1
  fi

  echo "Push to $branch failed (attempt $attempt/$max_attempts); refreshing the branch" >&2
  if git fetch origin "+refs/heads/${branch}:refs/remotes/origin/${branch}"; then
    if ! git merge-base --is-ancestor "origin/$branch" HEAD; then
      if ! git rebase "origin/$branch"; then
        git rebase --abort
        echo "The translation conflicts with a concurrent update to $branch" >&2
        exit 1
      fi
      continue
    fi
  fi
  sleep $((attempt * 2))
done
