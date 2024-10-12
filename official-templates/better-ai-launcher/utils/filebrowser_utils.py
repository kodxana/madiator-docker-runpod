import subprocess
import time

FILEBROWSER_PORT = 8181
filebrowser_process = None

def configure_filebrowser():
    try:
        subprocess.run('filebrowser config init', shell=True, check=True)
        subprocess.run('filebrowser config set --auth.method=json', shell=True, check=True)
        subprocess.run('filebrowser config set --baseurl /fileapp', shell=True, check=True)
        subprocess.run('filebrowser config set --root /workspace', shell=True, check=True)
        subprocess.run('filebrowser users add admin admin', shell=True, check=True)
        print("File Browser configured successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error configuring File Browser: {e}")
        return False

def start_filebrowser():
    global filebrowser_process
    if filebrowser_process is None or filebrowser_process.poll() is not None:
        filebrowser_process = subprocess.Popen(['filebrowser', '-r', '/workspace', '-a', '0.0.0.0', '-p', str(FILEBROWSER_PORT), '--baseurl', '/fileapp'])
        time.sleep(2)  # Give it a moment to start
        return filebrowser_process.poll() is None
    return False

def stop_filebrowser():
    global filebrowser_process
    if filebrowser_process and filebrowser_process.poll() is None:
        filebrowser_process.terminate()
        filebrowser_process.wait(timeout=10)
        filebrowser_process = None
        return True
    return False

def get_filebrowser_status():
    return 'running' if filebrowser_process and filebrowser_process.poll() is None else 'stopped'
