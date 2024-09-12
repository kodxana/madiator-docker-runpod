#!/bin/bash

# Function to download file
download_file() {
    local url="$1"
    local destination="$2"
    local token="$3"

    if [ -f "$destination" ]; then
        read -p "File $destination already exists. Overwrite? (y/n): " overwrite
        if [[ $overwrite != [Yy]* ]]; then
            echo "Skipping download of $destination"
            return
        fi
    fi

    if [ -n "$token" ]; then
        wget --header="Authorization: Bearer $token" -O "$destination" "$url"
    else
        wget -O "$destination" "$url"
    fi
}

# Check for Hugging Face token
if [ -z "$HF_TOKEN" ]; then
    read -p "Enter your Hugging Face token (press Enter to skip for public models): " HF_TOKEN
fi

# Menu for model selection
echo "Select Flux AI Model variant to install:"
echo "1. Single-file FP8 version (16GB VRAM)"
echo "2. Flux Schnell version (16GB VRAM)"
echo "3. Regular FP16 full version (24GB VRAM)"
read -p "Enter your choice (1-3): " model_choice

case $model_choice in
    1)
        download_file "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors" "/workspace/ComfyUI/models/unet/flux1-dev-fp8.safetensors" "$HF_TOKEN"
        ;;
    2)
        download_file "https://huggingface.co/Comfy-Org/flux1-schnell/resolve/main/flux1-schnell-fp8.safetensors" "/workspace/ComfyUI/models/unet/flux1-schnell-fp8.safetensors" "$HF_TOKEN"
        ;;
    3)
        if [ -z "$HF_TOKEN" ]; then
            echo "Hugging Face token is required for this model."
            exit 1
        fi
        download_file "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors" "/workspace/ComfyUI/models/unet/flux1-dev.safetensors" "$HF_TOKEN"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Download CLIP models
download_file "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors" "/workspace/ComfyUI/models/clip/clip_l.safetensors" "$HF_TOKEN"
download_file "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors" "/workspace/ComfyUI/models/clip/t5xxl_fp8_e4m3fn.safetensors" "$HF_TOKEN"

# Download VAE model
download_file "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors" "/workspace/ComfyUI/models/vae/ae.safetensors" "$HF_TOKEN"

echo "Installation complete!"