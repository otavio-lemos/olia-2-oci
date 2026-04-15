#!/bin/bash
# usage: ./generate_opencode.sh 10 compute/instances
# args: $1 = batch_size, $2 = category

BATCH=${1:-10}
CATEGORY=${2:-compute/instances}

SYSTEM_PROMPT='Você é um OCI Specialist. Responda em JSON com array de examples.'
PROMPT=$(cat <<EOF
Gere $BATCH exemplos sobre OCI: $CATEGORY.
Cada exemplo: question, answer, difficulty.
Responda apenas com JSON:
{
  \"examples\": [
    {\"question\": \"...\", \"answer\": \"...\", \"difficulty\": \"...\"}
  ]
}
EOF
)

echo '---'
echo opencode run --prompt \"$PROMPT\" --format json
echo '---'

opencode run --prompt. \"$PROMPT\" --format json 2>&1 | while read line; do
  if echo \"$line\" | grep -q '\"type\":\"text\"'; then
    echo \"$line\" | grep -o '\"text\":\"[^\"]*\"' | sed 's/\"text\":\"//;s/\"$//'
  fi
done