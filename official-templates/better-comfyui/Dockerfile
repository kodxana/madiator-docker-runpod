# Stage 1: Base Image
FROM madiator2011/better-base:cuda12.1 as base

ARG PYTHON_VERSION1=3.11
ARG TORCH=torch==2.3.0+cu121

# Stage 2: ComfyUI Installation
FROM base as comfyui-install

# Create virtual environment in /workspace/venv
RUN python -m venv /workspace/venv

# Set environment variables for the virtual environment
ENV VIRTUAL_ENV="/workspace/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Activate the virtual environment and install packages
RUN $VIRTUAL_ENV/bin/pip install --upgrade pip setuptools wheel && \
    if [ -n "${TORCH}" ]; then \
        $VIRTUAL_ENV/bin/pip install --no-cache-dir ${TORCH}; \
    fi && \
    git clone https://github.com/comfyanonymous/ComfyUI.git /ComfyUI && \
    $VIRTUAL_ENV/bin/pip install -r /ComfyUI/requirements.txt && \
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git /ComfyUI/custom_nodes/ComfyUI-Manager && \
    $VIRTUAL_ENV/bin/pip install -r /ComfyUI/custom_nodes/ComfyUI-Manager/requirements.txt && \
    $VIRTUAL_ENV/bin/pip install xformers accelerate wheel comfy-cli insightface && \
    $VIRTUAL_ENV/bin/pip install ipykernel ipywidgets && \
    $VIRTUAL_ENV/bin/python -m ipykernel install --name "python3" --display-name "Python 3 (Workspace Venv)"

# Stage 3: Model Setup
FROM comfyui-install as model-setup

# Create model and cache directories
RUN mkdir -p /root/.cache/huggingface /comfy-models

ARG INCLUDE_MODELS=false

# Download each model in a separate layer
RUN if [ "${INCLUDE_MODELS}" = "true" ]; then \
    wget -q --show-progress https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors -O /comfy-models/v1-5-pruned-emaonly.safetensors; \
    fi

RUN if [ "${INCLUDE_MODELS}" = "true" ]; then \
    wget -q --show-progress https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.safetensors -O /comfy-models/v2-1_768-ema-pruned.safetensors; \
    fi

RUN if [ "${INCLUDE_MODELS}" = "true" ]; then \
    wget -q --show-progress https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors -O /comfy-models/sd_xl_base_1.0.safetensors; \
    fi

RUN if [ "${INCLUDE_MODELS}" = "true" ]; then \
    wget -q --show-progress https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors -O /comfy-models/sd_xl_refiner_1.0.safetensors; \
    fi

# Verify models were downloaded
RUN if [ "${INCLUDE_MODELS}" = "true" ]; then \
    ls -lh /comfy-models; \
    fi

# Stage 4: Final Image
FROM comfyui-install as final

# Move virtual environment from /workspace/venv to /venv
RUN mv /workspace/venv /venv

# Copy models if they were included
COPY --from=model-setup /comfy-models /comfy-models

# Set environment variables for runtime
ENV VIRTUAL_ENV="/workspace/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the README.md
COPY README.md /usr/share/nginx/html/README.md

# NGINX Proxy
COPY --from=proxy nginx.conf /etc/nginx/nginx.conf
COPY --from=proxy readme.html /usr/share/nginx/html/readme.html

# Copy all necessary scripts
COPY pre_start.sh /pre_start.sh
COPY --from=scripts start.sh /
RUN chmod +x /start.sh
RUN chmod +x /pre_start.sh
COPY comfyui_extras.ipynb /comfyui_extras.ipynb

# CMD
CMD [ "/start.sh" ]