#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to print colorized feedback
print_feedback() {
    GREEN='\033[0;32m'
    NC='\033[0m' # No Color
    echo -e "${GREEN}[Forge Startup]:${NC} $1"
}

# Function to run rsync with progress bar and optimizations
rsync_with_progress() {
    rsync -aHvx --info=progress2 --ignore-existing --update --stats "$@"
}

# Check if the NO_SYNC variable is set to true
if [ "${NO_SYNC}" == "true" ]; then
    print_feedback "Skipping sync and startup as per environment variable setting."
    exec bash -c 'sleep infinity'
fi

print_feedback "Starting A1111 setup..."

# Extract the virtual environment if it doesn't exist
if [ ! -d "/workspace/ba1111" ]; then
    print_feedback "Extracting virtual environment..."
    mkdir -p /workspace/ba1111
    tar -xzf /ba1111.tar.gz -C /workspace/ba1111
else
    print_feedback "Virtual environment already exists, skipping extraction..."
fi

# Activate the virtual environment
source /workspace/ba1111/bin/activate

# Check if Stable Diffusion WebUI a111 exists in the workspace
if [ ! -d "/workspace/stable-diffusion-webui" ] || [ -z "$(ls -A /workspace/stable-diffusion-webui)" ]; then
    print_feedback "Stable Diffusion WebUI A1111 not found or empty. Syncing all files..."
    rsync_with_progress /stable-diffusion-webui/ /workspace/stable-diffusion-webui/
    print_feedback "Initial sync completed."
else
    print_feedback "Stable Diffusion WebUI A1111 found. Skipping sync to preserve user modifications."
fi

# Change to the a111 directory
cd /workspace/stable-diffusion-webui

# Modify webui.sh to allow running as root, only if needed
print_feedback "Checking webui.sh configuration..."
if grep -q "can_run_as_root=0" webui.sh; then
    print_feedback "Modifying webui.sh to allow running as root..."
    sed -i 's/can_run_as_root=0/can_run_as_root=1/' webui.sh
else
    print_feedback "webui.sh already configured to run as root or configuration not found."
fi

# Create logs directory if it doesn't exist
mkdir -p /workspace/logs

# Start webui-user.sh and log output
print_feedback "Starting webui-user.sh..."
./webui.sh -f > >(tee /workspace/logs/a1111.log) 2>&1 &