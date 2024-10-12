#!/bin/bash

app_name=$1
download_url=$2
workspace_dir="/workspace"
app_dir="${workspace_dir}/${app_name}"
tar_file="${workspace_dir}/${app_name}.tar.gz"

echo "Starting download of ${app_name} venv..."

aria2c -x 16 -s 16 \
    --summary-interval=1 \
    --download-result=full \
    "${download_url}" -d "${workspace_dir}" -o "${app_name}.tar.gz" 2>&1 | \
    sed -u 's/^\[#[0-9a-f]\+ \([0-9.]\+[KMGT]\?iB\)\/\([0-9.]\+[KMGT]\?iB\)(\([0-9]\+%\))/Download progress: \1 of \2 (\3)/' | \
    sed -u 's/^Download Progress Summary/\nDownload Progress Summary/' | \
    sed -u 's/^Download Results:/\nDownload Results:/' | \
    sed -u 's/\x1b\[[0-9;]*m//g'  # Remove ANSI color codes

if [ $? -eq 0 ] && [ -f "${tar_file}" ]; then
    echo "Download completed successfully. Starting extraction..."
    echo "Creating directory: ${app_dir}"
    mkdir -p "${app_dir}"
    echo "Extracting ${tar_file} to ${app_dir}..."
    echo "This process may take several minutes. Please be patient."
    
    # Check if pv is available
    if command -v pv >/dev/null 2>&1; then
        # Use pv to show progress
        pv "${tar_file}" | tar -xzf - -C "${app_dir}" 2>&1 | \
        while read -r line; do
            echo "Extraction progress: $line"
        done
    else
        # Fallback to a more basic method if pv is not available
        tar -xzvf "${tar_file}" -C "${app_dir}" | \
        while read -r line; do
            echo "Extracting: $line"
        done
    fi
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "Extraction completed successfully."
        rm "${tar_file}"
        echo "Temporary file removed."
        echo "Installation of ${app_name} completed successfully."
        echo "Please refresh the page to see the changes and start using ${app_name}."
    else
        echo "Error: Extraction failed."
        exit 1
    fi
else
    echo "Error: Download failed or file not found."
    echo "Download URL: ${download_url}"
    echo "Target file: ${tar_file}"
    ls -l "${workspace_dir}"
    exit 1
fi