import multiprocessing
import os

# Bind inside the container; external port mapping is done by Docker
bind = "0.0.0.0:5000"

# Poller-safe worker model:
# - 1 worker to avoid multiple poller threads
# - multiple threads for concurrency
workers = 1
threads = 4

# Don’t preload the app, to avoid any surprise with background threads
preload_app = False

# Graceful timeout values
timeout = 30
graceful_timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Optional: tag this process for diagnostics
proc_name = "logexp-gunicorn"
