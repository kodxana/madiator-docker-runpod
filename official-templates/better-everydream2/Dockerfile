FROM madiator2011/better-pytorch:cuda12.1
ARG DEBIAN_FRONTEND=noninteractive
ARG TORCH
ARG TORCHVISION
ARG TORCHAUDIO
ARG PYTHON_VERSION

# Use bash shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV SHELL=/bin/bash
ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH="/usr/local/cuda-12.1/targets/x86_64-linux/lib/"

# Create workspace directory
WORKDIR /

# Install any additional packages not included in the base image
RUN apt-get update --yes && \
    apt-get upgrade --yes && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen

# Clone EveryDream2trainer repository
WORKDIR /root
RUN git clone https://github.com/victorchall/EveryDream2trainer

# Add requirements files and install Python packages from the cloned repository
RUN pip install --upgrade --no-cache-dir pip && \
    pip install ${TORCH} torchvision torchaudio && \ 
    pip install --no-deps xformers==0.0.22.post7 && \
    pip install --no-cache-dir -r /root/EveryDream2trainer/docker/requirements-build.txt && \
    pip install --no-cache-dir -r /root/EveryDream2trainer/docker/requirements-runtime.txt

# Copy pre_start.sh script to the image
COPY pre_start.sh /pre_start.sh
RUN chmod +x /pre_start.sh

# Copy notebook
COPY Train_RunPod.ipynb /root/EveryDream2trainer/Train_RunPod.ipynb

# Start Scripts
COPY --from=scripts start.sh /
RUN chmod +x /start.sh

# Set the default command for the container
CMD [ "/start.sh" ]
