# filename: gunicorn.conf.py

bind = "0.0.0.0:5000"

workers = 1
threads = 4
preload_app = False

timeout = 30
graceful_timeout = 30
keepalive = 2

accesslog = "-"
errorlog = "-"
loglevel = "info"

proc_name = "logexp-gunicorn"
