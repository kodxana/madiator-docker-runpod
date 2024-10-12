# Use the specified base image
FROM madiator2011/better-base:cuda12.1 as base

# Install Python 3.11, set it as default, and remove Python 3.10
RUN apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils aria2 git \
    pv git rsync zstd libtcmalloc-minimal4 bc nginx ffmpeg && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    apt-get remove -y python3.10 python3.10-minimal libpython3.10-minimal libpython3.10-stdlib && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.11
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.11 get-pip.py && \
    rm get-pip.py

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN python3.11 -mpip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Install File Browser
RUN curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash

# Set environment variables for production
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV APP_PATH=/app/app.py

# Expose the port Nginx will listen on
EXPOSE 7222

# Copy the README.md
COPY README.md /usr/share/nginx/html/README.md

# NGINX configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY readme.html /usr/share/nginx/html/readme.html

# Create a directory for static files
RUN mkdir -p /app/static

# Copy the Poddy animation files to the static directory
COPY poddy.png /app/static/poddy.png
COPY mushroom.png /app/static/mushroom.png
COPY snake.png /app/static/snake.png
COPY poddy-song.mp3 /app/static/poddy-song.mp3

# Copy all necessary scripts
COPY --from=scripts start.sh /
COPY pre_start.sh /pre_start.sh
RUN chmod +x /pre_start.sh /start.sh
# Copy the download_venv.sh script and make it executable
COPY download_venv.sh /app/download_venv.sh
RUN chmod +x /app/download_venv.sh

# CMD
CMD ["/start.sh"]