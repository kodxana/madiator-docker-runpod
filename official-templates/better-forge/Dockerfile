# Stage 1: Base Image
FROM madiator2011/better-base:cuda12.1 as base

ARG PYTHON_VERSION1=3.11

# Install additional packages
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y pv git rsync libtcmalloc-minimal4 bc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Stage 2: Forge Installation
FROM base as forge-install

# Create virtual environment with the correct path
RUN mkdir -p /workspace && python -m venv /workspace/bforge

# Set environment variables for the virtual environment
ENV VIRTUAL_ENV="/workspace/bforge"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Clone Stable Diffusion WebUI Forge and additional repositories
RUN git clone https://github.com/lllyasviel/stable-diffusion-webui-forge.git /stable-diffusion-webui-forge && \
    mkdir -p /stable-diffusion-webui-forge/repositories && \
    git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui-assets.git /stable-diffusion-webui-forge/repositories/stable-diffusion-webui-assets && \
    git clone https://github.com/lllyasviel/huggingface_guess.git /stable-diffusion-webui-forge/repositories/huggingface_guess && \
    git clone https://github.com/salesforce/BLIP.git /stable-diffusion-webui-forge/repositories/BLIP && \
    rm /stable-diffusion-webui-forge/webui-user.sh

# Activate the virtual environment and install packages
RUN $VIRTUAL_ENV/bin/pip install --upgrade pip setuptools wheel && \
    $VIRTUAL_ENV/bin/pip install -r /stable-diffusion-webui-forge/requirements_versions.txt && \
    $VIRTUAL_ENV/bin/pip install -U xformers --index-url https://download.pytorch.org/whl/cu121 && \
    $VIRTUAL_ENV/bin/pip install accelerate wheel && \
    $VIRTUAL_ENV/bin/pip install ipykernel ipywidgets && \
    $VIRTUAL_ENV/bin/pip install "https://github.com/openai/CLIP/archive/d50d76daa670286dd6cacf3bcd80b5e4823fc8e1.zip" && \
    $VIRTUAL_ENV/bin/pip install "https://github.com/mlfoundations/open_clip/archive/bb6e834e9c70d9c27d0dc3ecedeebeaeb1ffad6b.zip" && \
    $VIRTUAL_ENV/bin/pip install fvcore mediapipe onnxruntime svglib insightface && \
    $VIRTUAL_ENV/bin/pip install "https://github.com/huchenlei/HandRefinerPortable/releases/download/v1.0.1/handrefinerportable-2024.2.12.0-py2.py3-none-any.whl" && \
    $VIRTUAL_ENV/bin/pip install "https://github.com/huchenlei/Depth-Anything/releases/download/v1.0.0/depth_anything-2024.1.22.0-py2.py3-none-any.whl" && \
    $VIRTUAL_ENV/bin/pip install "https://github.com/MackinationsAi/UDAV2-ControlNet/releases/download/v1.0.0/depth_anything_v2-2024.7.1.0-py2.py3-none-any.whl" && \
    $VIRTUAL_ENV/bin/pip install bitsandbytes==0.43.3 && \
    $VIRTUAL_ENV/bin/python -m ipykernel install --name "python3" --display-name "Python 3 (Better Forge Venv)"

# Create tar archive of the virtual environment
RUN tar -czf /bforge.tar.gz -C /workspace/bforge .

# Remove the original venv to save space in the image
RUN rm -rf /workspace/bforge

# Stage 3: Final Image
FROM forge-install as final

# Set environment variables for runtime
ENV VIRTUAL_ENV="/workspace/bforge"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the README.md
COPY README.md /usr/share/nginx/html/README.md

# NGINX Proxy
COPY --from=proxy nginx.conf /etc/nginx/nginx.conf
COPY --from=proxy readme.html /usr/share/nginx/html/readme.html

# Copy all necessary scripts
COPY --from=scripts start.sh /
COPY pre_start.sh /pre_start.sh
COPY webui-user.sh /stable-diffusion-webui-forge/webui-user.sh
RUN chmod +x /start.sh /pre_start.sh /stable-diffusion-webui-forge/webui-user.sh
COPY settings.json /root/.local/share/code-server/User/settings.json

# Copy the tar archive and Stable Diffusion WebUI Forge
COPY --from=forge-install /bforge.tar.gz /bforge.tar.gz
COPY --from=forge-install /stable-diffusion-webui-forge /stable-diffusion-webui-forge

# Welcome Message
COPY --from=logo runpod.txt /etc/runpod.txt
RUN echo 'cat /etc/runpod.txt' >> /root/.bashrc && \
    echo 'echo -e "\nFor detailed documentation and guides, please visit:\n\033[1;34mhttps://docs.runpod.io/\033[0m and \033[1;34mhttps://blog.runpod.io/\033[0m\n\n"' >> /root/.bashrc

# CMD
CMD [ "/start.sh" ]