# Stage 1: Base Image
FROM madiator2011/better-pytorch:cuda12.1 as base

ARG PYTHON_VERSION1
ARG TORCH

# Install PyTorch if specified
RUN if [ -n "${TORCH}" ]; then \
    pip install --upgrade --no-cache-dir ${TORCH}; \
    fi 

# Stage 2: ComfyUI Installation
FROM base as comfyui-install

# Create and activate virtual environment for ComfyUI installation
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

RUN git clone https://github.com/comfyanonymous/ComfyUI.git && \
    cd /ComfyUI && \
    pip install -r requirements.txt && \
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git custom_nodes/ComfyUI-Manager && \
    cd custom_nodes/ComfyUI-Manager && \
    pip install -r requirements.txt && \
    pip install -U xformers --index-url https://download.pytorch.org/whl/cu121

# Stage 3: Model Setup and Final Image
FROM comfyui-install as final

# Create model and cache directories
RUN mkdir -p /root/.cache/huggingface && mkdir -p /comfy-models

# Download models directly
RUN wget -q --show-progress https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors -O /comfy-models/v1-5-pruned-emaonly.safetensors && \
    wget -q --show-progress https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.safetensors -O /comfy-models/v2-1_768-ema-pruned.safetensors && \
    wget -q --show-progress https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors -O /comfy-models/sd_xl_base_1.0.safetensors && \
    wget -q --show-progress https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors -O /comfy-models/sd_xl_refiner_1.0.safetensors

# Verify models were downloaded
RUN ls -lh /comfy-models

# NGINX Proxy
COPY --from=proxy nginx.conf /etc/nginx/nginx.conf
COPY --from=proxy readme.html /usr/share/nginx/html/readme.html

# Copy the README.md
COPY README.md /usr/share/nginx/html/README.md

# Set environment variables for runtime
ENV PATH="/workspace/venv/bin:$PATH"
ENV VIRTUAL_ENV="/workspace/venv"

# Start Scripts
COPY pre_start.sh /pre_start.sh

# Start Scripts
COPY --from=scripts start.sh /
RUN chmod +x /start.sh

CMD [ "/start.sh" ]