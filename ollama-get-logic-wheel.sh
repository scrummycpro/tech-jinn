#!/bin/bash

# Function to create the SQLite database and table if they don't exist
create_database() {
  sqlite3 tech-career.db <<EOF
CREATE TABLE IF NOT EXISTS logic (
  id INTEGER PRIMARY KEY,
  timestamp TEXT,
  prompt TEXT,
  response TEXT
);
EOF
}

# Function to query Ollama and insert response into SQLite
store_response() {
  local prompt="$1"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

  # Query Ollama for a response
  response=$(curl -s http://localhost:11434/api/generate -d '{
    "model": "llama3",
    "prompt": "'"in the terms of is, is not, should not be associated with explain $prompt in the form of 500 word college paper, and give some SOP and debates,controversies and keywords to associate, also include any references, the answer should explain what it is, its opposite and its associations, and antonyms; also gibe a detail mnemonic device and a detailed reverse quintain, reference the key components involved."'",
    "stream": false
  }' | jq -r .response)

  # Escape single quotes in the prompt and response
  escaped_prompt=$(echo "$prompt" | sed "s/'/''/g")
  escaped_response=$(echo "$response" | sed "s/'/''/g")

  # Insert the timestamp, prompt, and response into the SQLite database
  sqlite3 tech-career.db <<EOF
INSERT INTO logic-wheel (timestamp, prompt, response) VALUES ('$timestamp', '$escaped_prompt', '$escaped_response');
EOF
}

# Check if a prompt was provided
if [ -z "$1" ]; then
  echo "Usage: $0 <prompt>"
  exit 1
fi

# Create the database and table if they don't exist
create_database

# Call the function with the provided prompt
store_response "$1"