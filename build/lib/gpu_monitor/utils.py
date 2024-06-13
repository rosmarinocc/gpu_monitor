# gpu_monitor/utils.py

import os
import sys
import subprocess
import configparser
import logging
import functools
from gpu_monitor.config import CONFIG_FILE, LOG_FILE, PID_FILE

logger = logging.getLogger(__name__)

def daemonize(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
        
        os.setsid()

        _pid = os.fork()
        if _pid > 0:
            sys.exit()
        
        os.umask(0)
        sys.stdout.flush()
        sys.stderr.flush()

        redirect_std_to_log()
        os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
        with open(PID_FILE, 'w+') as f:
            f.write(str(os.getpid()))
        with open(PID_FILE, 'r') as f:
            written_pid = f.read().strip()
            logger.info(f"GPU-Monitor PID written to {PID_FILE}: {written_pid}")
        
        return func(*args, **kwargs)
    return wrapper

def redirect_std_to_log():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open('/dev/null', 'r') as read_null_fd, open(LOG_FILE, 'a') as log_fd:
        os.dup2(read_null_fd.fileno(), sys.stdin.fileno())
        os.dup2(log_fd.fileno(), sys.stdout.fileno())
        os.dup2(log_fd.fileno(), sys.stderr.fileno())

def read_config():
    config = configparser.ConfigParser()
    try:
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError("Configuration file not found.")
        config.read(CONFIG_FILE)
        return config['EMAIL']
    except FileNotFoundError as e:
        logger.warning(f"{e}. Please run 'gpu_monitor configure' to set up the configuration.")
        return None
    except Exception as e:
        logger.error(f"An error occurred while reading the configuration file: {e}")
        return None
    

def write_config(from_addr, smtp_passwd, to_addr):
    config = configparser.ConfigParser()
    config['EMAIL'] = {
        'FROM_ADDR': from_addr,
        'FROM_SMTP_PASSWD': smtp_passwd,
        'TO_ADDR': to_addr
    }
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    logger.info("Configuration saved successfully.")

def getGpuMemory():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used',
                                 '--format=csv,noheader,nounits'], capture_output=True, text=True)
        gpu_available_list = [(float(usage)/(1024)) < 1.0 for usage in result.stdout.strip().split('\n')]
        logger.info("GPU memory usage retrieved successfully.")
        return gpu_available_list
    except Exception as e:
        logger.error(f"Error in getGpuMemory: {e}")
        return []
