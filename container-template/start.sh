#!/bin/bash
set -e  # Exit the script if any statement returns a non-true return value

# ---------------------------------------------------------------------------- #
#                          Function Definitions                                #
# ---------------------------------------------------------------------------- #

# Start nginx service
start_nginx() {
    echo "Starting Nginx service..."
    service nginx start
}

# Execute script if exists
execute_script() {
    local script_path=$1
    local script_msg=$2
    if [[ -f ${script_path} ]]; then
        echo "${script_msg}"
        bash ${script_path}
    fi
}

# Setup SSH
setup_ssh() {
    if [[ $PUBLIC_KEY ]]; then
        echo "Setting up SSH..."
        mkdir -p ~/.ssh
        echo "$PUBLIC_KEY" >> ~/.ssh/authorized_keys
        chmod 700 -R ~/.ssh

        for key_type in rsa dsa ecdsa ed25519; do
            key_path="/etc/ssh/ssh_host_${key_type}_key"
            if [ ! -f ${key_path} ]; then
                ssh-keygen -t ${key_type} -f ${key_path} -q -N ''
                echo "${key_type^^} key fingerprint:"
                ssh-keygen -lf ${key_path}.pub
            fi
        done

        service ssh start

        echo "SSH host keys:"
        for key in /etc/ssh/*.pub; do
            echo "Key: $key"
            ssh-keygen -lf $key
        done
    fi
}

# Export environment variables
export_env_vars() {
    echo "Exporting environment variables..."
    printenv | grep -E '^RUNPOD_|^PATH=|^_=' | awk -F = '{ print "export " $1 "=\"" $2 "\"" }' >> /etc/rp_environment
    echo 'source /etc/rp_environment' >> ~/.bashrc
}

# Start code-server
start_code_server() {
    echo "Starting code-server..."
    nohup code-server --bind-addr 0.0.0.0:7777 --auth none --disable-telemetry /workspace &> /code-server.log &
    echo "code-server started"
}

# ---------------------------------------------------------------------------- #
#                               Main Program                                   #
# ---------------------------------------------------------------------------- #

start_nginx
setup_ssh
start_code_server
export_env_vars

echo "Pod Started"


execute_script "/pre_start.sh" "Running post-start script..."

echo "Start script(s) finished, pod is ready to use."

sleep infinity
