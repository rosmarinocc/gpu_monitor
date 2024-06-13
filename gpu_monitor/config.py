# gpu_monitor/config.py

import os

CONFIG_DIR = os.path.expanduser('~/.gpu_monitor')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'gpu_monitor_config.ini')
LOG_FILE = os.path.join(CONFIG_DIR, 'gpu_monitor.log')
PID_FILE = os.path.join(CONFIG_DIR, 'gpu_monitor_pid.log')
INTERVAL = 60


