import subprocess
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import time
import fire
import configparser
import os
import sys
import threading

### usage ###
# gpu_monitor configure
# gpu_monitor help
# gpu_monitor monitor_all
# gpu_monitor monitor <GPU_INDEX>

CONFIG_FILE = os.path.join(os.path.expanduser("~"), '.gpu_monitor_config.ini')
INTERVAL = 60

def read_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        raise Exception("Configuration file not found. Please run 'gpu_monitor configure' to set up the configuration.")
    config.read(CONFIG_FILE)
    return config['EMAIL']

def write_config(from_addr, smtp_passwd, to_addr):
    config = configparser.ConfigParser()
    config['EMAIL'] = {
        'FROM_ADDR': from_addr,
        'FROM_SMTP_PASSWD': smtp_passwd,
        'TO_ADDR': to_addr
    }
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def configure():
    from_addr = input("Please enter FROM_ADDR (your email address): ")
    smtp_passwd = input("Please enter SMTP_PASSWD (your email password): ")
    to_addr = input("Please enter TO_ADDR (recipient's email address): ")
    write_config(from_addr, smtp_passwd, to_addr)
    print("Configuration saved successfully.")

def getGpuMemory():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used',
                                '--format=csv,noheader,nounits'], capture_output=True, text=True)
        gpu_available_list = [
            (float(usage)/(1024)) < 1.0 for usage in result.stdout.strip().split('\n')]
        return gpu_available_list

    except Exception as e:
        print("Error:", e)
        return []

class EmailSender():
    def __init__(self):
        try:
            config = read_config()
            self.from_addr = config['FROM_ADDR']
            self.password = config['FROM_SMTP_PASSWD']
            self.to_addr = config['TO_ADDR']
            self.smtp_server = 'smtp.qq.com'
        except Exception as e:
            print(e)
            sys.exit(1)

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def send_msg(self, msg):
        msg = MIMEText(msg, 'plain', 'utf-8')
        msg['From'] = self._format_addr(f'GPU-Monitor <{self.from_addr}>')
        msg['To'] = self._format_addr(f'Recipient <{self.to_addr}>')
        msg['Subject'] = Header('Server GPUs are available!', 'utf-8').encode()
        server = smtplib.SMTP(self.smtp_server, 25)
        server.set_debuglevel(1)
        server.login(self.from_addr, self.password)
        server.sendmail(self.from_addr, [self.to_addr], msg.as_string())
        server.quit()

def monitor_all():
    def run_monitor_all():
        email_sender = EmailSender()
        while True:
            res = getGpuMemory()
            if True in res:
                msg = f"GPUs available on the server: {[idx for idx, r in enumerate(res) if r]}"
                email_sender.send_msg(msg)
                return msg
            time.sleep(INTERVAL)
    
    thread = threading.Thread(target=run_monitor_all)
    thread.daemon = True
    thread.start()
    print("Monitoring all GPUs in the background...")

def monitor(no: int):
    def run_monitor(no):
        email_sender = EmailSender()
        while True:
            res = getGpuMemory()
            if res[no]:
                msg = f"GPU {no} is now available, the program has finished running."
                email_sender.send_msg(msg)
                return msg
            time.sleep(INTERVAL)
    
    thread = threading.Thread(target=run_monitor, args=(no,))
    thread.daemon = True
    thread.start()
    print(f"Monitoring GPU {no} in the background...")

def help():
    usage = """gpu_monitor <command> [<args>]
Commands:
    configure         Configure email settings
    monitor_all       Monitor all GPUs
    monitor <index>   Monitor a specific GPU by its index"""
    print(usage)

def main():
    fire.Fire({
        'configure': configure,
        'monitor_all': monitor_all,
        'monitor': monitor,
        'help': help
    })

if __name__ == '__main__':
    main()
