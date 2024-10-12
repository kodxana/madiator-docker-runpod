# Gunicorn configuration file
import multiprocessing

# Worker settings
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker'
worker_connections = 1000
timeout = 300

# Server socket
bind = '0.0.0.0:7222'

# Logging
loglevel = 'info'
accesslog = '-'
errorlog = '-'

# Misc
daemon = False