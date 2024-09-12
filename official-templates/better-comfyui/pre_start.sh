#!/bin/bash

# Set a default TERM if it's not set
if [ -z "$TERM" ]; then
    export TERM=xterm-256color
fi

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
    rsync -aHvx --info=progress2 --ignore-existing --update --stats "$@"
}

# Check for required commands
for cmd in rsync; do
    if ! command -v $cmd &> /dev/null; then
        echo "$cmd could not be found, please install it."
        exit 1
    fi
done

LOG_FILE="/workspace/comfyui.log"

# Copy the notebook and install-flux.sh script to the /workspace directory
print_feedback "Copying notebook and install script to /workspace..."
cp /comfyui_extras.ipynb /workspace/
cp /install-flux.sh /workspace/

# Check if the NO_SYNC variable is set to true
if [ "${NO_SYNC}" == "true" ]; then
    print_feedback "Skipping sync and startup as per environment variable setting."
    exec bash -c 'sleep infinity'
fi

print_feedback "Starting ComfyUI setup..."

print_feedback "Syncing virtual environment..."
VIRTUAL_ENV="/workspace/runpod-venvs/better-comfyui"
SOURCE_VENV="/venv"
NUM_CORES=$(nproc)

if [ ! -d "$VIRTUAL_ENV" ]; then
    clear
    echo -e "\e[1;33m"
    cat << "EOF"
 _____________________________________
|                                     |
|  !!! ATTENTION - FIRST TIME SYNC !!!|
|                                     |
|  This process will take ~10 minutes |
|_____________________________________|

EOF
    echo -e "\e[0m"
    
    mkdir -p "$VIRTUAL_ENV"
    
    # Start background process to show progress
    (
        while true; do
            for s in / - \\ \|; do
                printf "\r\033[1;31m[%s] \033[1;37mSYNC IN PROGRESS - PLEASE WAIT\033[0m" "$s"
                sleep 0.5
            done
        done
    ) &
    PROGRESS_PID=$!

    # Perform the sync
    rsync -aHx --info=progress2 --stats --exclude='*.pyc' --exclude='__pycache__' "$SOURCE_VENV/" "$VIRTUAL_ENV/"

    # Stop the progress indicator
    kill $PROGRESS_PID
    wait $PROGRESS_PID 2>/dev/null

    clear
    echo -e "\e[1;32m"
    cat << "EOF"
 _____________________________________
|                                     |
|        SYNC COMPLETED SUCCESS       |
|_____________________________________|

EOF
    echo -e "\e[0m"
else
    print_feedback "Subsequent sync: Updating venv without overwriting existing files..."
    rsync -aHx --info=progress2 --stats --exclude='*.pyc' --exclude='__pycache__' --ignore-existing --update "$SOURCE_VENV/" "$VIRTUAL_ENV/"
fi

print_feedback "Activating virtual environment..."
source "$VIRTUAL_ENV/bin/activate"

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
    exec python main.py --listen --port 3000 --enable-cors-header $CUSTOM_ARGS 2>&1 | tee -a $LOG_FILE
else
    exec python main.py --listen --port 3000 --enable-cors-header 2>&1 | tee -a $LOG_FILE
fi
