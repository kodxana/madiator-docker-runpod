# Stage 1: Base Image
FROM madiator2011/better-base:cuda12.1 as base

ARG PYTHON_VERSION1=3.11

# Install additional packages including zstd
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y pv git rsync libtcmalloc-minimal4 bc zstd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Stage 2: A1111 Installation
FROM base as a1111-install

# Create virtual environment with the correct path
RUN mkdir -p /workspace && python -m venv /workspace/ba1111

# Set environment variables for the virtual environment
ENV VIRTUAL_ENV="/workspace/ba1111"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Clone AUTOMATIC1111 Stable Diffusion WebUI and additional repositories
RUN git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git /stable-diffusion-webui && \
    mkdir -p /stable-diffusion-webui/repositories && \
    git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui-assets.git /stable-diffusion-webui/repositories/stable-diffusion-webui-assets && \
    git clone https://github.com/Stability-AI/stablediffusion.git /stable-diffusion-webui/repositories/stable-diffusion && \
    git clone https://github.com/Stability-AI/stablediffusion.git /stable-diffusion-webui/repositories/stable-diffusion-stability-ai && \
    git clone https://github.com/Stability-AI/generative-models.git /stable-diffusion-webui/repositories/generative-models && \
    git clone https://github.com/crowsonkb/k-diffusion.git /stable-diffusion-webui/repositories/k-diffusion && \
    git clone https://github.com/salesforce/BLIP.git /stable-diffusion-webui/repositories/BLIP && \
    rm /stable-diffusion-webui/webui-user.sh

# Activate the virtual environment and install packages
RUN $VIRTUAL_ENV/bin/pip install --upgrade pip setuptools wheel && \
    $VIRTUAL_ENV/bin/pip install -r /stable-diffusion-webui/requirements_versions.txt && \
    $VIRTUAL_ENV/bin/pip install accelerate wheel && \
    $VIRTUAL_ENV/bin/pip install ipykernel ipywidgets && \
    $VIRTUAL_ENV/bin/pip install "https://github.com/openai/CLIP/archive/d50d76daa670286dd6cacf3bcd80b5e4823fc8e1.zip" && \
    $VIRTUAL_ENV/bin/pip install "https://github.com/mlfoundations/open_clip/archive/bb6e834e9c70d9c27d0dc3ecedeebeaeb1ffad6b.zip" && \
    $VIRTUAL_ENV/bin/pip install bitsandbytes==0.43.3 && \
    $VIRTUAL_ENV/bin/python -m ipykernel install --name "python3" --display-name "Python 3 (Better A1111 Venv)" && \
    $VIRTUAL_ENV/bin/pip install -U xformers --index-url https://download.pytorch.org/whl/cu121

# Create tar archive and compress with zstd
RUN tar -cf - -C /workspace ba1111 | zstd -T0 -f -o /ba1111.tar.zst

# Remove the original venv to save space in the image
RUN rm -rf /workspace/ba1111

# New stage for uploading ba1111.tar.zst to MinIO
FROM a1111-install as uploader

# Install boto3
RUN pip install boto3

# Set MinIO configuration using environment variables
ENV MINIO_ENDPOINT=https://s3.madiator.com
ENV MINIO_ACCESS_KEY=""
ENV MINIO_SECRET_KEY=""
ENV MINIO_BUCKET="better"

# Copy the upload script
COPY upload_to_minio.py /upload_to_minio.py

# Set the entrypoint to the upload script
ENTRYPOINT ["python", "/upload_to_minio.py"]

# Stage 3: Final Image
FROM a1111-install as final

# Set environment variables for runtime
ENV VIRTUAL_ENV="/workspace/ba1111"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the README.md
COPY README.md /usr/share/nginx/html/README.md

# NGINX Proxy
COPY --from=proxy nginx.conf /etc/nginx/nginx.conf
COPY --from=proxy readme.html /usr/share/nginx/html/readme.html

# Copy all necessary scripts
COPY --from=scripts start.sh /
COPY pre_start.sh /pre_start.sh
COPY webui-user.sh /stable-diffusion-webui/webui-user.sh
RUN chmod +x /start.sh /pre_start.sh /stable-diffusion-webui/webui-user.sh
COPY settings.json /root/.local/share/code-server/User/settings.json

# Copy the tar.zst archive and Stable Diffusion WebUI
COPY --from=a1111-install /ba1111.tar.zst /ba1111.tar.zst
COPY --from=a1111-install /stable-diffusion-webui /stable-diffusion-webui

# Welcome Message
COPY --from=logo runpod.txt /etc/runpod.txt
RUN echo 'cat /etc/runpod.txt' >> /root/.bashrc && \
    echo 'echo -e "\nFor detailed documentation and guides, please visit:\n\033[1;34mhttps://docs.runpod.io/\033[0m and \033[1;34mhttps://blog.runpod.io/\033[0m\n\n"' >> /root/.bashrc

# CMD
CMD [ "/start.sh" ]