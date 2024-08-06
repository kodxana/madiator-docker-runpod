ARG BASE_IMAGE
FROM ${BASE_IMAGE} AS base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV SHELL=/bin/bash

# Set the working directory
WORKDIR /

# Create workspace directory
RUN mkdir /workspace

# Update, upgrade, install packages,
RUN apt-get update --yes && \
    apt-get upgrade --yes && \
    apt install --yes --no-install-recommends \
        git wget curl bash libgl1 software-properties-common \
        openssh-server nginx rsync nano ffmpeg tmux && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen

RUN pip install --upgrade --no-cache-dir pip

COPY ms-toolsai.jupyter-2024.7.0.vsix /tmp/ms-toolsai.jupyter-2024.7.0.vsix

# Install code-server and extensions
RUN curl -fsSL https://code-server.dev/install.sh | sh && \
    code-server --install-extension ms-python.python && \
    code-server --install-extension ms-toolsai.vscode-jupyter-powertoys && \
    code-server --install-extension /tmp/ms-toolsai.jupyter-2024.7.0.vsix
    
RUN rm /tmp/ms-toolsai.jupyter-2024.7.0.vsix

# Pre-install Jupyter kernel and OhMyRunPod
RUN pip install ipykernel && \
    python -m ipykernel install --name "python3" --display-name "Python 3" && \
    pip install OhMyRunPod

# Remove existing SSH host keys
RUN rm -f /etc/ssh/ssh_host_*

# Copy necessary files
COPY settings.json /root/.local/share/code-server/User/settings.json

# Final stage: minimal image
FROM ${BASE_IMAGE}

COPY --from=base / /

# NGINX Proxy
COPY --from=proxy nginx.conf /etc/nginx/nginx.conf
COPY --from=proxy readme.html /usr/share/nginx/html/readme.html

# Copy the README.md
COPY README.md /usr/share/nginx/html/README.md

# Start Scripts
COPY --from=scripts start.sh /
RUN chmod +x /start.sh

# Welcome Message
COPY --from=logo runpod.txt /etc/runpod.txt
RUN echo 'cat /etc/runpod.txt' >> /root/.bashrc && \
    echo 'echo -e "\nFor detailed documentation and guides, please visit:\n\033[1;34mhttps://docs.runpod.io/\033[0m and \033[1;34mhttps://blog.runpod.io/\033[0m\n\n"' >> /root/.bashrc

# Set the default command for the container
CMD [ "/start.sh" ]
