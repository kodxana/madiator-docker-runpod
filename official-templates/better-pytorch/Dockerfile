ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG TORCH
ARG PYTHON_VERSION

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV SHELL=/bin/bash

# Set the working directory
WORKDIR /

# Create workspace directory
RUN mkdir /workspace

# Update, upgrade, install packages, install python if PYTHON_VERSION is specified, clean up
RUN apt-get update --yes && \
    apt-get upgrade --yes && \
    apt install --yes --no-install-recommends git wget curl bash libgl1 software-properties-common openssh-server nginx rsync nano ffmpeg tmux && \
    if [ -n "${PYTHON_VERSION}" ]; then \
        add-apt-repository ppa:deadsnakes/ppa && \
        apt install "python${PYTHON_VERSION}-dev" "python${PYTHON_VERSION}-venv" -y --no-install-recommends; \
    fi && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen

# Set up Python and pip only if PYTHON_VERSION is specified
RUN if [ -n "${PYTHON_VERSION}" ]; then \
        ln -s /usr/bin/python${PYTHON_VERSION} /usr/bin/python && \
        rm /usr/bin/python3 && \
        ln -s /usr/bin/python${PYTHON_VERSION} /usr/bin/python3 && \
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
        python get-pip.py; \
    fi

RUN pip install --upgrade --no-cache-dir pip

# Install PyTorch only if TORCH is specified
RUN if [ -n "${TORCH}" ]; then pip install --upgrade --no-cache-dir ${TORCH}; fi 

# Install code-server
RUN curl -fsSL https://code-server.dev/install.sh | sh

# Copy VSIX files to the Docker image
COPY vsix/*.vsix /tmp/

# Install VS Code extensions from local VSIX files
RUN code-server --install-extension /tmp/RSIP-Vision.nvidia-smi-plus-1.0.1.vsix && \
    code-server --install-extension /tmp/vscode-ext.sync-rsync-0.36.0.vsix

# Install VS Code extensions
RUN code-server --install-extension ms-python.python
RUN code-server --install-extension ms-toolsai.jupyter
RUN code-server --install-extension ms-toolsai.vscode-jupyter-powertoys

# Pre-install Jupyter kernel
RUN pip install ipykernel
RUN python -m ipykernel install --name "python3" --display-name "Python 3"

# Install OhMyRunPod
RUN pip install OhMyRunPod

# Remove existing SSH host keys
RUN rm -f /etc/ssh/ssh_host_*

COPY settings.json /root/.local/share/code-server/User/settings.json

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
RUN echo 'cat /etc/runpod.txt' >> /root/.bashrc
RUN echo 'echo -e "\nFor detailed documentation and guides, please visit:\n\033[1;34mhttps://docs.runpod.io/\033[0m and \033[1;34mhttps://blog.runpod.io/\033[0m\n\n"' >> /root/.bashrc

# Expose port for code-server
EXPOSE 8080

# Set the default command for the container
CMD [ "/start.sh" ]
