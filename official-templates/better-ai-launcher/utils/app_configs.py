import os
import xml.etree.ElementTree as ET
import requests

def fetch_app_info():
    url = "https://better.s3.madiator.com/"
    response = requests.get(url)
    root = ET.fromstring(response.content)

    app_info = {}
    for content in root.findall('{http://s3.amazonaws.com/doc/2006-03-01/}Contents'):
        key = content.find('{http://s3.amazonaws.com/doc/2006-03-01/}Key').text
        size = int(content.find('{http://s3.amazonaws.com/doc/2006-03-01/}Size').text)
        app_name = key.split('/')[0]
        
        if app_name in ['ba1111', 'bcomfy', 'bforge']:
            app_info[app_name] = {
                'download_url': f"https://better.s3.madiator.com/{key}",
                'size': size
            }

    return app_info

app_configs = {
    'bcomfy': {
        'name': 'Better Comfy UI',
        'command': 'cd /workspace/bcomfy && . ./bin/activate && cd /workspace/ComfyUI && python main.py --listen --port 3000 --enable-cors-header',
        'venv_path': '/workspace/bcomfy',
        'app_path': '/workspace/ComfyUI',
        'port': 3000,
    },
    'bforge': {
        'name': 'Better Forge',
        'command': 'cd /workspace/bforge && . ./bin/activate && cd /workspace/stable-diffusion-webui-forge && ./webui.sh -f --listen --enable-insecure-extension-access --api --port 7862',
        'venv_path': '/workspace/bforge',
        'app_path': '/workspace/stable-diffusion-webui-forge',
        'port': 7862,
    },
    'ba1111': {
        'name': 'Better A1111',
        'command': 'cd /workspace/ba1111 && . ./bin/activate && cd /workspace/stable-diffusion-webui && ./webui.sh -f --listen --enable-insecure-extension-access --api --port 7863',
        'venv_path': '/workspace/ba1111',
        'app_path': '/workspace/stable-diffusion-webui',
        'port': 7863,
    }
}

def update_app_configs():
    app_info = fetch_app_info()
    for app_name, info in app_info.items():
        if app_name in app_configs:
            app_configs[app_name].update(info)

def get_app_configs():
    return app_configs

def add_app_config(app_name, config):
    app_configs[app_name] = config

def remove_app_config(app_name):
    if app_name in app_configs:
        del app_configs[app_name]

# Update app_configs when this module is imported
update_app_configs()
