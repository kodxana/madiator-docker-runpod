# Base Image
FROM madiator2011/better-pytorch:cuda12.1

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Download and install Ollama
RUN curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/bin/ollama && \
    chmod +x /usr/bin/ollama

COPY settings.json /root/.local/share/code-server/User/settings.json
COPY tasks.json /root/.local/share/code-server/User/tasks.json

# Start Scripts
COPY --from=scripts start.sh /
RUN chmod +x /start.sh

# Set environment variables for runtime
ENV OLLAMA_HOST=0.0.0.0
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV LD_LIBRARY_PATH=/usr/local/nvidia/lib:/usr/local/nvidia/lib64
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV NVIDIA_VISIBLE_DEVICES=all

# Expose the required port
EXPOSE 11434


CMD ["/start.sh"]
