from gevent import monkey
monkey.patch_all()

import os
import threading
import time
from flask import Flask, render_template, jsonify, request
from flask_sock import Sock
import json
import signal
import shutil
import subprocess
import traceback

from utils.ssh_utils import setup_ssh, save_ssh_password, get_ssh_password, check_ssh_config, SSH_CONFIG_FILE
from utils.filebrowser_utils import configure_filebrowser, start_filebrowser, stop_filebrowser, get_filebrowser_status, FILEBROWSER_PORT
from utils.app_utils import (
    run_app, update_process_status, check_app_directories, get_app_status,
    force_kill_process_by_name, update_webui_user_sh, save_install_status,
    get_install_status, download_and_unpack_venv, fix_custom_nodes, is_process_running,
)
from utils.websocket_utils import send_websocket_message, active_websockets
from utils.app_configs import get_app_configs, add_app_config, remove_app_config

app = Flask(__name__)
sock = Sock(app)

RUNPOD_POD_ID = os.environ.get('RUNPOD_POD_ID', 'localhost')

running_processes = {}

app_configs = get_app_configs()

S3_BASE_URL = "https://better.s3.madiator.com/"

SETTINGS_FILE = '/workspace/.app_settings.json'

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {'auto_generate_ssh_password': False}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

def check_running_processes():
    while True:
        for app_name in list(running_processes.keys()):
            update_process_status(app_name, running_processes)
            current_status = get_app_status(app_name, running_processes)
            send_websocket_message('status_update', {app_name: current_status})
        time.sleep(5)

@app.route('/')
def index():
    settings = load_settings()
    
    # Determine the current SSH authentication method
    with open(SSH_CONFIG_FILE, 'r') as f:
        ssh_config = f.read()
    current_auth_method = 'key' if 'PasswordAuthentication no' in ssh_config else 'password'

    # Get the current SSH password if it exists
    ssh_password = get_ssh_password()
    ssh_password_status = 'set' if ssh_password else 'not_set'

    app_status = {}
    for app_name, config in app_configs.items():
        dirs_ok, message = check_app_directories(app_name, app_configs)
        status = get_app_status(app_name, running_processes)
        install_status = get_install_status(app_name)
        app_status[app_name] = {
            'name': config['name'],
            'dirs_ok': dirs_ok,
            'message': message,
            'port': config['port'],
            'status': status,
            'installed': dirs_ok,
            'install_status': install_status,
            'is_bcomfy': app_name == 'bcomfy'  # Add this line
        }
    filebrowser_status = get_filebrowser_status()
    return render_template('index.html', 
                           apps=app_configs, 
                           app_status=app_status, 
                           pod_id=RUNPOD_POD_ID, 
                           RUNPOD_PUBLIC_IP=os.environ.get('RUNPOD_PUBLIC_IP'),
                           RUNPOD_TCP_PORT_22=os.environ.get('RUNPOD_TCP_PORT_22'),
                           settings=settings,
                           current_auth_method=current_auth_method,
                           ssh_password=ssh_password,
                           ssh_password_status=ssh_password_status,
                           filebrowser_status=filebrowser_status)

@app.route('/start/<app_name>')
def start_app(app_name):
    dirs_ok, message = check_app_directories(app_name, app_configs)
    if not dirs_ok:
        return jsonify({'status': 'error', 'message': message})
    
    if app_name in app_configs and get_app_status(app_name, running_processes) == 'stopped':
        # Update webui-user.sh for Forge and A1111
        if app_name in ['bforge', 'ba1111']:
            update_webui_user_sh(app_name, app_configs)

        command = app_configs[app_name]['command']
        threading.Thread(target=run_app, args=(app_name, command, running_processes)).start()
        return jsonify({'status': 'started'})
    return jsonify({'status': 'already_running'})

@app.route('/stop/<app_name>')
def stop_app(app_name):
    if app_name in running_processes and get_app_status(app_name, running_processes) == 'running':
        try:
            pgid = os.getpgid(running_processes[app_name]['pid'])
            os.killpg(pgid, signal.SIGTERM)
            
            for _ in range(10):
                if not is_process_running(running_processes[app_name]['pid']):
                    break
                time.sleep(1)
            
            if is_process_running(running_processes[app_name]['pid']):
                os.killpg(pgid, signal.SIGKILL)
            
            running_processes[app_name]['status'] = 'stopped'
            return jsonify({'status': 'stopped'})
        except ProcessLookupError:
            running_processes[app_name]['status'] = 'stopped'
            return jsonify({'status': 'already_stopped'})
    return jsonify({'status': 'not_running'})

@app.route('/status')
def get_status():
    return jsonify({app_name: get_app_status(app_name, running_processes) for app_name in app_configs})

@app.route('/logs/<app_name>')
def get_logs(app_name):
    if app_name in running_processes:
        return jsonify({'logs': running_processes[app_name]['log'][-100:]})
    return jsonify({'logs': []})

@app.route('/kill_all', methods=['POST'])
def kill_all():
    try:
        for app_key in app_configs:
            if get_app_status(app_key, running_processes) == 'running':
                stop_app(app_key)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/force_kill/<app_name>', methods=['POST'])
def force_kill_app(app_name):
    try:
        success, message = force_kill_process_by_name(app_name, app_configs)
        if success:
            return jsonify({'status': 'killed', 'message': message})
        else:
            return jsonify({'status': 'error', 'message': message})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@sock.route('/ws')
def websocket(ws):
    active_websockets.add(ws)
    try:
        while True:
            message = ws.receive()
            data = json.loads(message)
            
            if data['type'] == 'heartbeat':
                ws.send(json.dumps({'type': 'heartbeat'}))
            else:
                # Handle other message types
                pass
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        active_websockets.remove(ws)

def send_heartbeat():
    while True:
        time.sleep(60)  # Send heartbeat every 60 seconds (1 minute)
        send_websocket_message('heartbeat', {})

# Start heartbeat thread
threading.Thread(target=send_heartbeat, daemon=True).start()

@app.route('/install/<app_name>', methods=['POST'])
def install_app(app_name):
    try:
        success, message = download_and_unpack_venv(app_name)
        if success:
            return jsonify({'status': 'success', 'message': message})
        else:
            return jsonify({'status': 'error', 'message': message})
    except Exception as e:
        error_message = f"Installation error for {app_name}: {str(e)}\n{traceback.format_exc()}"
        app.logger.error(error_message)
        return jsonify({'status': 'error', 'message': error_message}), 500

@app.route('/fix_custom_nodes/<app_name>', methods=['POST'])
def fix_custom_nodes_route(app_name):
    success, message = fix_custom_nodes(app_name)
    if success:
        return jsonify({'status': 'success', 'message': message})
    else:
        return jsonify({'status': 'error', 'message': message})

@app.route('/set_ssh_password', methods=['POST'])
def set_ssh_password():
    try:
        data = request.json
        new_password = data.get('password')
        
        if not new_password:
            return jsonify({'status': 'error', 'message': 'No password provided'})
        
        print("Attempting to set new password...")
        
        # Use chpasswd to set the password
        process = subprocess.Popen(['chpasswd'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate(input=f"root:{new_password}\n")
        
        if process.returncode != 0:
            raise Exception(f"Failed to set password: {error}")
        
        # Save the new password
        save_ssh_password(new_password)
        
        # Configure SSH to allow root login with password
        print("Configuring SSH to allow root login with a password...")
        subprocess.run(["sed", "-i", 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/', "/etc/ssh/sshd_config"], check=True)
        subprocess.run(["sed", "-i", 's/#PasswordAuthentication no/PasswordAuthentication yes/', "/etc/ssh/sshd_config"], check=True)
        
        # Restart SSH service to apply changes
        print("Restarting SSH service...")
        subprocess.run(['service', 'ssh', 'restart'], check=True)
        print("SSH service restarted successfully.")
        
        print("SSH Configuration Updated and Password Set.")
        
        return jsonify({'status': 'success', 'message': 'SSH password set successfully. Note: Key-based authentication is more secure.'})
    except Exception as e:
        error_message = f"Error in set_ssh_password: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({'status': 'error', 'message': error_message})

@app.route('/start_filebrowser')
def start_filebrowser_route():
    if start_filebrowser():
        return jsonify({'status': 'started'})
    return jsonify({'status': 'already_running'})

@app.route('/stop_filebrowser')
def stop_filebrowser_route():
    if stop_filebrowser():
        return jsonify({'status': 'stopped'})
    return jsonify({'status': 'already_stopped'})

@app.route('/filebrowser_status')
def filebrowser_status_route():
    return jsonify({'status': get_filebrowser_status()})

@app.route('/add_app_config', methods=['POST'])
def add_new_app_config():
    data = request.json
    app_name = data.get('app_name')
    config = data.get('config')
    if app_name and config:
        add_app_config(app_name, config)
        return jsonify({'status': 'success', 'message': f'App {app_name} added successfully'})
    return jsonify({'status': 'error', 'message': 'Invalid data provided'})

@app.route('/remove_app_config/<app_name>', methods=['POST'])
def remove_existing_app_config(app_name):
    if app_name in app_configs:
        remove_app_config(app_name)
        return jsonify({'status': 'success', 'message': f'App {app_name} removed successfully'})
    return jsonify({'status': 'error', 'message': f'App {app_name} not found'})

def setup_shared_models():
    shared_models_dir = '/workspace/shared_models'
    model_types = ['Stable-diffusion', 'VAE', 'Lora', 'ESRGAN']

    # Create shared models directory if it doesn't exist
    os.makedirs(shared_models_dir, exist_ok=True)

    for model_type in model_types:
        shared_model_path = os.path.join(shared_models_dir, model_type)
        
        # Create shared model type directory if it doesn't exist
        os.makedirs(shared_model_path, exist_ok=True)

    # Create a README file in the shared models directory
    readme_path = os.path.join(shared_models_dir, 'README.txt')
    if not os.path.exists(readme_path):
        with open(readme_path, 'w') as f:
            f.write("Upload your models to the appropriate folders:\n\n")
            f.write("- Stable-diffusion: for Stable Diffusion models\n")
            f.write("- VAE: for VAE models\n")
            f.write("- Lora: for LoRA models\n")
            f.write("- ESRGAN: for ESRGAN upscaling models\n\n")
            f.write("These models will be automatically linked to all supported apps.")

    print(f"Shared models directory created at {shared_models_dir}")
    print("Shared models setup completed.")

    return shared_models_dir

def update_model_symlinks():
    shared_models_dir = '/workspace/shared_models'
    apps = {
        'stable-diffusion-webui': '/workspace/stable-diffusion-webui/models',
        'stable-diffusion-webui-forge': '/workspace/stable-diffusion-webui-forge/models',
        'ComfyUI': '/workspace/ComfyUI/models'
    }
    model_types = ['Stable-diffusion', 'VAE', 'Lora', 'ESRGAN']

    for model_type in model_types:
        shared_model_path = os.path.join(shared_models_dir, model_type)
        
        if not os.path.exists(shared_model_path):
            continue

        for app, app_models_dir in apps.items():
            if app == 'ComfyUI':
                if model_type == 'Stable-diffusion':
                    app_model_path = os.path.join(app_models_dir, 'checkpoints')
                elif model_type == 'Lora':
                    app_model_path = os.path.join(app_models_dir, 'loras')
                elif model_type == 'ESRGAN':
                    app_model_path = os.path.join(app_models_dir, 'upscale_models')
                else:
                    app_model_path = os.path.join(app_models_dir, model_type.lower())
            else:
                app_model_path = os.path.join(app_models_dir, model_type)
            
            # Create the app model directory if it doesn't exist
            os.makedirs(app_model_path, exist_ok=True)

            # Create symlinks for each file in the shared model directory
            for filename in os.listdir(shared_model_path):
                src = os.path.join(shared_model_path, filename)
                dst = os.path.join(app_model_path, filename)
                if os.path.isfile(src) and not os.path.exists(dst):
                    os.symlink(src, dst)

    print("Model symlinks updated.")

def update_symlinks_periodically():
    while True:
        update_model_symlinks()
        time.sleep(300)  # Check every 5 minutes

def start_symlink_update_thread():
    thread = threading.Thread(target=update_symlinks_periodically, daemon=True)
    thread.start()

def recreate_symlinks():
    shared_models_dir = '/workspace/shared_models'
    apps = {
        'stable-diffusion-webui': '/workspace/stable-diffusion-webui/models',
        'stable-diffusion-webui-forge': '/workspace/stable-diffusion-webui-forge/models',
        'ComfyUI': '/workspace/ComfyUI/models'
    }
    model_types = ['Stable-diffusion', 'VAE', 'Lora', 'ESRGAN']

    for model_type in model_types:
        shared_model_path = os.path.join(shared_models_dir, model_type)
        
        if not os.path.exists(shared_model_path):
            continue

        for app, app_models_dir in apps.items():
            if app == 'ComfyUI':
                if model_type == 'Stable-diffusion':
                    app_model_path = os.path.join(app_models_dir, 'checkpoints')
                elif model_type == 'Lora':
                    app_model_path = os.path.join(app_models_dir, 'loras')
                elif model_type == 'ESRGAN':
                    app_model_path = os.path.join(app_models_dir, 'upscale_models')
                else:
                    app_model_path = os.path.join(app_models_dir, model_type.lower())
            else:
                app_model_path = os.path.join(app_models_dir, model_type)
            
            # Remove existing symlinks
            if os.path.islink(app_model_path):
                os.unlink(app_model_path)
            elif os.path.isdir(app_model_path):
                shutil.rmtree(app_model_path)
            
            # Create the app model directory if it doesn't exist
            os.makedirs(app_model_path, exist_ok=True)

            # Create symlinks for each file in the shared model directory
            for filename in os.listdir(shared_model_path):
                src = os.path.join(shared_model_path, filename)
                dst = os.path.join(app_model_path, filename)
                if os.path.isfile(src) and not os.path.exists(dst):
                    os.symlink(src, dst)

    return "Symlinks recreated successfully."

@app.route('/recreate_symlinks', methods=['POST'])
def recreate_symlinks_route():
    try:
        message = recreate_symlinks()
        return jsonify({'status': 'success', 'message': message})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/create_shared_folders', methods=['POST'])
def create_shared_folders():
    try:
        shared_models_dir = '/workspace/shared_models'
        model_types = ['Stable-diffusion', 'VAE', 'Lora', 'ESRGAN']

        # Create shared models directory if it doesn't exist
        os.makedirs(shared_models_dir, exist_ok=True)

        for model_type in model_types:
            shared_model_path = os.path.join(shared_models_dir, model_type)
            
            # Create shared model type directory if it doesn't exist
            os.makedirs(shared_model_path, exist_ok=True)

        # Create a README file in the shared models directory
        readme_path = os.path.join(shared_models_dir, 'README.txt')
        if not os.path.exists(readme_path):
            with open(readme_path, 'w') as f:
                f.write("Upload your models to the appropriate folders:\n\n")
                f.write("- Stable-diffusion: for Stable Diffusion models\n")
                f.write("- VAE: for VAE models\n")
                f.write("- Lora: for LoRA models\n")
                f.write("- ESRGAN: for ESRGAN upscaling models\n\n")
                f.write("These models will be automatically linked to all supported apps.")

        return jsonify({'status': 'success', 'message': 'Shared model folders created successfully.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    shared_models_path = setup_shared_models()
    print(f"Shared models directory: {shared_models_path}")
    
    if setup_ssh():
        print("SSH setup completed successfully.")
    else:
        print("Failed to set up SSH. Please check the logs.")
    
    print("Configuring File Browser...")
    if configure_filebrowser():
        print("File Browser configuration completed successfully.")
        print("Attempting to start File Browser...")
        if start_filebrowser():
            print("File Browser started successfully.")
        else:
            print("Failed to start File Browser. Please check the logs.")
    else:
        print("Failed to configure File Browser. Please check the logs.")
    
    threading.Thread(target=check_running_processes, daemon=True).start()
    
    # Start the thread to periodically update model symlinks
    start_symlink_update_thread()
    
    app.run(debug=True, host='0.0.0.0', port=7223)