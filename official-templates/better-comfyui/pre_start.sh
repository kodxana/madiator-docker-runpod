#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to print colorized feedback
print_feedback() {
    GREEN='\033[0;32m'
    NC='\033[0m' # No Color
    echo -e "${GREEN}[ComfyUI Startup]:${NC} $1"
}

# Function to run rsync with progress bar
rsync_with_progress() {
    stdbuf -i0 -o0 -e0 rsync -au --info=progress2 "$@" | stdbuf -i0 -o0 -e0 tr '\r' '\n' | stdbuf -i0 -o0 -e0 grep -oP '\d+%|\d+.\d+[mMgG]' | tqdm --bar-format='{l_bar}{bar}' --total=100 --unit='%' > /dev/null
}

print_feedback "Starting ComfyUI setup..."

print_feedback "Syncing virtual environment..."
rsync_with_progress /venv/ /workspace/venv/

print_feedback "Activating virtual environment..."
source /workspace/venv/bin/activate

export PYTHONUNBUFFERED=1

print_feedback "Syncing ComfyUI files..."
rsync_with_progress --remove-source-files /ComfyUI/ /workspace/ComfyUI/

print_feedback "Creating symbolic links for model checkpoints..."
ln -sf /comfy-models/* /workspace/ComfyUI/models/checkpoints/

print_feedback "Changing to ComfyUI directory..."
cd /workspace/ComfyUI

print_feedback "Starting ComfyUI server..."
print_feedback "ComfyUI will be available at http://0.0.0.0:3000"
exec /workspace/venv/bin/python main.py --listen --port 3000