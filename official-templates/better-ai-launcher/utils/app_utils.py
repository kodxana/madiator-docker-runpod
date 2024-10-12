import os
import subprocess
import psutil
import signal
import re
import json
import git
import requests
import traceback
from tqdm import tqdm
import xml.etree.ElementTree as ET
import time

INSTALL_STATUS_FILE = '/tmp/install_status.json'

def is_process_running(pid):
    try:
        process = psutil.Process(pid)
        return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:
        return False

def run_app(app_name, command, running_processes):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, preexec_fn=os.setsid)
    running_processes[app_name] = {
        'process': process,
        'pid': process.pid,
        'log': [],
        'status': 'running'
    }
    
    for line in process.stdout:
        running_processes[app_name]['log'].append(line.strip())
        if len(running_processes[app_name]['log']) > 1000:
            running_processes[app_name]['log'] = running_processes[app_name]['log'][-1000:]
    
    running_processes[app_name]['status'] = 'stopped'

def update_process_status(app_name, running_processes):
    if app_name in running_processes:
        if is_process_running(running_processes[app_name]['pid']):
            running_processes[app_name]['status'] = 'running'
        else:
            running_processes[app_name]['status'] = 'stopped'

def check_app_directories(app_name, app_configs):
    app_config = app_configs.get(app_name)
    if not app_config:
        return False, f"App '{app_name}' not found in configurations."
    
    venv_path = app_config['venv_path']
    app_path = app_config['app_path']
    
    if not os.path.exists(venv_path):
        return False, f"Virtual environment not found: {venv_path}"
    
    if not os.path.exists(app_path):
        return False, f"Application directory not found: {app_path}"
    
    return True, "App directories found."

def get_app_status(app_name, running_processes):
    if app_name in running_processes:
        update_process_status(app_name, running_processes)
        return running_processes[app_name]['status']
    return 'stopped'

def find_and_kill_process_by_port(port):
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            try:
                process = psutil.Process(conn.pid)
                for child in process.children(recursive=True):
                    child.kill()
                process.kill()
                return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    return False

def force_kill_process_by_name(app_name, app_configs):
    app_config = app_configs.get(app_name)
    if not app_config:
        return False, f"App '{app_name}' not found in configurations."

    port = app_config['port']
    killed = find_and_kill_process_by_port(port)

    if killed:
        return True, f"{app_name} processes have been forcefully terminated."
    else:
        return False, f"No running processes found for {app_name} on port {port}."

def update_webui_user_sh(app_name, app_configs):
    app_config = app_configs.get(app_name)
    if not app_config:
        return

    webui_user_sh_path = os.path.join(app_config['app_path'], 'webui-user.sh')
    if not os.path.exists(webui_user_sh_path):
        return

    with open(webui_user_sh_path, 'r') as file:
        content = file.read()

    # Use regex to remove --port and its value
    updated_content = re.sub(r'--port\s+\d+', '', content)

    with open(webui_user_sh_path, 'w') as file:
        file.write(updated_content)

def save_install_status(app_name, status, progress=0, stage=''):
    data = {
        'status': status,
        'progress': progress,
        'stage': stage
    }
    try:
        with open(INSTALL_STATUS_FILE, 'r') as f:
            all_statuses = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_statuses = {}
    
    all_statuses[app_name] = data
    
    with open(INSTALL_STATUS_FILE, 'w') as f:
        json.dump(all_statuses, f)

def get_install_status(app_name):
    try:
        with open(INSTALL_STATUS_FILE, 'r') as f:
            all_statuses = json.load(f)
        return all_statuses.get(app_name, {'status': 'not_started', 'progress': 0, 'stage': ''})
    except (FileNotFoundError, json.JSONDecodeError):
        return {'status': 'not_started', 'progress': 0, 'stage': ''}

def download_and_unpack_venv(app_name, app_configs, send_websocket_message):
    app_config = app_configs.get(app_name)
    if not app_config:
        return False, f"App '{app_name}' not found in configurations."

    venv_path = app_config['venv_path']
    app_path = app_config['app_path']
    download_url = app_config['download_url']
    total_size = app_config['size']
    tar_filename = os.path.basename(download_url)
    workspace_dir = '/workspace'
    downloaded_file = os.path.join(workspace_dir, tar_filename)

    try:
        save_install_status(app_name, 'in_progress', 0, 'Downloading')
        send_websocket_message('install_log', {'app_name': app_name, 'log': f'Starting download of {total_size / (1024 * 1024):.2f} MB...'})

        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        block_size = 8192
        downloaded_size = 0
        start_time = time.time()

        with open(downloaded_file, 'wb') as file:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    
                    if elapsed_time > 0:
                        speed = downloaded_size / elapsed_time
                        percentage = (downloaded_size / total_size) * 100
                        eta = (total_size - downloaded_size) / speed if speed > 0 else 0
                        
                        send_websocket_message('install_progress', {
                            'app_name': app_name,
                            'percentage': round(percentage, 2),
                            'speed': f"{speed / (1024 * 1024):.2f} MB/s",
                            'eta': f"{eta:.0f}",
                            'stage': 'Downloading',
                            'downloaded': f"{downloaded_size / (1024 * 1024):.2f} MB"
                        })

        send_websocket_message('install_log', {'app_name': app_name, 'log': 'Download completed. Starting unpacking...'})
        send_websocket_message('install_progress', {'app_name': app_name, 'percentage': 100, 'stage': 'Download Complete'})
        
        # Ensure the venv directory exists
        os.makedirs(venv_path, exist_ok=True)

        # Unpack the tar.gz file
        send_websocket_message('install_progress', {'app_name': app_name, 'percentage': 0, 'stage': 'Unpacking'})
        unpack_command = f"tar -xzvf {downloaded_file} -C {venv_path}"
        process = subprocess.Popen(unpack_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        total_files = sum(1 for _ in subprocess.Popen(f"tar -tvf {downloaded_file}", shell=True, stdout=subprocess.PIPE).stdout)
        files_processed = 0
        
        for line in process.stdout:
            files_processed += 1
            percentage = min(int((files_processed / total_files) * 100), 100)
            send_websocket_message('install_progress', {
                'app_name': app_name,
                'percentage': percentage,
                'stage': 'Unpacking',
                'processed': files_processed,
                'total': total_files
            })
            send_websocket_message('install_log', {'app_name': app_name, 'log': f"Unpacking: {line.strip()}"})
        
        process.wait()
        if process.returncode != 0:
            error_message = f"Unpacking failed: {process.stderr.read() if process.stderr else 'Unknown error'}"
            send_websocket_message('install_complete', {'app_name': app_name, 'status': 'error', 'message': error_message})
            save_install_status(app_name, 'failed', 0, 'Failed')
            return False, error_message
        
        send_websocket_message('install_progress', {'app_name': app_name, 'percentage': 100, 'stage': 'Unpacking Complete'})

        # Clone the repository if it doesn't exist
        if not os.path.exists(app_path):
            send_websocket_message('install_log', {'app_name': app_name, 'log': 'Cloning repository...'})
            
            repo_url = ''
            if app_name == 'bcomfy':
                repo_url = 'https://github.com/comfyanonymous/ComfyUI.git'
            elif app_name == 'bforge':
                repo_url = 'https://github.com/lllyasviel/stable-diffusion-webui-forge.git'
            elif app_name == 'ba1111':
                repo_url = 'https://github.com/AUTOMATIC1111/stable-diffusion-webui.git'
            
            try:
                git.Repo.clone_from(repo_url, app_path, progress=lambda op_code, cur_count, max_count, message: send_websocket_message('install_log', {
                    'app_name': app_name,
                    'log': f"Cloning: {cur_count}/{max_count} {message}"
                }))
                send_websocket_message('install_log', {'app_name': app_name, 'log': 'Repository cloned successfully.'})

                # Clone ComfyUI-Manager for Better ComfyUI
                if app_name == 'bcomfy':
                    custom_nodes_path = os.path.join(app_path, 'custom_nodes')
                    os.makedirs(custom_nodes_path, exist_ok=True)
                    comfyui_manager_path = os.path.join(custom_nodes_path, 'ComfyUI-Manager')
                    if not os.path.exists(comfyui_manager_path):
                        send_websocket_message('install_log', {'app_name': app_name, 'log': 'Cloning ComfyUI-Manager...'})
                        git.Repo.clone_from('https://github.com/ltdrdata/ComfyUI-Manager.git', comfyui_manager_path)
                        send_websocket_message('install_log', {'app_name': app_name, 'log': 'ComfyUI-Manager cloned successfully.'})

            except git.exc.GitCommandError as e:
                send_websocket_message('install_log', {'app_name': app_name, 'log': f'Error cloning repository: {str(e)}'})
                return False, f"Error cloning repository: {str(e)}"

        # Clean up the downloaded file
        send_websocket_message('install_log', {'app_name': app_name, 'log': 'Cleaning up...'})
        os.remove(downloaded_file)
        send_websocket_message('install_log', {'app_name': app_name, 'log': 'Installation complete.'})

        save_install_status(app_name, 'completed', 100, 'Completed')
        send_websocket_message('install_complete', {'app_name': app_name, 'status': 'success', 'message': "Virtual environment installed successfully."})
        return True, "Virtual environment installed successfully."
    except requests.RequestException as e:
        error_message = f"Download failed: {str(e)}"
        send_websocket_message('install_complete', {'app_name': app_name, 'status': 'error', 'message': error_message})
        save_install_status(app_name, 'failed', 0, 'Failed')
        return False, error_message
    except Exception as e:
        error_message = f"Installation failed: {str(e)}\n{traceback.format_exc()}"
        save_install_status(app_name, 'failed', 0, 'Failed')
        send_websocket_message('install_complete', {'app_name': app_name, 'status': 'error', 'message': error_message})
        return False, error_message

def fix_custom_nodes(app_name, app_configs):
    if app_name != 'bcomfy':
        return False, "This operation is only available for Better ComfyUI."
    
    venv_path = app_configs['bcomfy']['venv_path']
    app_path = app_configs['bcomfy']['app_path']
    
    try:
        # Activate the virtual environment and run the commands
        activate_venv = f"source {venv_path}/bin/activate"
        set_default_command = f"comfy --skip-prompt --no-enable-telemetry set-default {app_path}"
        restore_dependencies_command = "comfy node restore-dependencies"
        
        full_command = f"{activate_venv} && {set_default_command} && {restore_dependencies_command}"
        
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, executable='/bin/bash')
        output, _ = process.communicate()
        
        if process.returncode == 0:
            return True, f"Custom nodes fixed successfully. Output: {output.decode('utf-8')}"
        else:
            return False, f"Error fixing custom nodes. Output: {output.decode('utf-8')}"
    except Exception as e:
        return False, f"Error fixing custom nodes: {str(e)}"