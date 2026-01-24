# filename: beamfoundry/gunicorn.conf.py

import logging as pylogging
import sys

loglevel = "info"
accesslog = "-"
errorlog = "-"

# Forward Python logs to stdout so Docker can capture them
root = pylogging.getLogger()
root.setLevel(pylogging.INFO)

handler = pylogging.StreamHandler(sys.stdout)
handler.setLevel(pylogging.INFO)

formatter = pylogging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
handler.setFormatter(formatter)

root.addHandler(handler)

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
