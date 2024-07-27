#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to print colorized feedback
print_feedback() {
    GREEN='\033[0;32m'
    NC='\033[0m' # No Color
    echo -e "${GREEN}[ComfyUI Startup]:${NC} $1"
}

# Function to run rsync with progress bar and optimizations
rsync_with_progress() {
    rsync -aHvx --info=progress2 "$@"
}

# Check for required commands
for cmd in rsync; do
    if ! command -v $cmd &> /dev/null; then
        echo "$cmd could not be found, please install it."
        exit 1
    fi
done

LOG_FILE="/workspace/comfyui.log"

print_feedback "Starting ComfyUI setup..."

print_feedback "Syncing virtual environment..."
rsync_with_progress /venv/ /workspace/venv/

print_feedback "Activating virtual environment..."
export VIRTUAL_ENV="/workspace/venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
source /workspace/venv/bin/activate

export PYTHONUNBUFFERED=1

print_feedback "Syncing ComfyUI files..."
rsync_with_progress /ComfyUI/ /workspace/ComfyUI/

print_feedback "Creating symbolic links for model checkpoints..."
ln -sf /comfy-models/* /workspace/ComfyUI/models/checkpoints/

print_feedback "Changing to ComfyUI directory..."
cd /workspace/ComfyUI

print_feedback "Starting ComfyUI server..."
print_feedback "ComfyUI will be available at http://0.0.0.0:3000"

# Check if CUSTOM_ARGS is set and not empty
if [ -n "$CUSTOM_ARGS" ]; then
    exec /workspace/venv/bin/python main.py --listen --port 3000 $CUSTOM_ARGS 2>&1 | tee -a $LOG_FILE
else
    exec /workspace/venv/bin/python main.py --listen --port 3000 2>&1 | tee -a $LOG_FILE
fi