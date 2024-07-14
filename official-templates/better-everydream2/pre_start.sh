#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to print colorized feedback
print_feedback() {
    GREEN='\033[0;32m'
    NC='\033[0m' # No Color
    echo -e "${GREEN}[EveryDream2trainer Startup]:${NC} $1"
}

# Function to run rsync with progress bar
rsync_with_progress() {
    stdbuf -i0 -o0 -e0 rsync -au --info=progress2 "$@" | stdbuf -i0 -o0 -e0 tr '\r' '\n' | stdbuf -i0 -o0 -e0 grep -oP '\d+%|\d+.\d+[mMgG]' | tqdm --bar-format='{l_bar}{bar}' --total=100 --unit='%' > /dev/null
}

# Check for required commands
for cmd in stdbuf rsync tr grep tqdm; do
    if ! command -v $cmd &> /dev/null; then
        echo "$cmd could not be found, please install it."
        exit 1
    fi
done

print_feedback "Starting EveryDream2trainer setup..."

print_feedback "Syncing EveryDream2trainer files..."
rsync_with_progress --remove-source-files /root/EveryDream2trainer/ /workspace/

print_feedback "Setup complete."
