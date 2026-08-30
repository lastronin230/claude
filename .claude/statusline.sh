#!/bin/sh
input=$(cat)
model=$(echo "$input" | jq -r '.model.display_name')
dir=$(echo "$input" | jq -r '.workspace.current_dir')
project=$(basename "$dir")
branch=$(git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null)
used=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
max_t=$(echo "$input" | jq -r '.context_window.context_window_size // 0')

if [ "$max_t" -gt 0 ] 2>/dev/null; then
  max_k=$((max_t / 1000))
  filled=$((used / 10))
  empty=$((10 - filled))
  bar=''
  i=0
  while [ $i -lt $filled ]; do
    bar="${bar}█"
    i=$((i + 1))
  done
  i=0
  while [ $i -lt $empty ]; do
    bar="${bar}░"
    i=$((i + 1))
  done

  if [ "$used" -lt 50 ]; then
    c='\033[32m'
  elif [ "$used" -lt 80 ]; then
    c='\033[33m'
  else
    c='\033[31m'
  fi

  if [ -n "$branch" ]; then
    printf "\033[34m%s\033[0m | ${c}[%s] %s%%/%sk\033[0m | %s (\033[35m%s\033[0m)" \
      "$model" "$bar" "$used" "$max_k" "$project" "$branch"
  else
    printf "\033[34m%s\033[0m | ${c}[%s] %s%%/%sk\033[0m | %s" \
      "$model" "$bar" "$used" "$max_k" "$project"
  fi
else
  printf "\033[34m%s\033[0m | %s" "$model" "$project"
fi
