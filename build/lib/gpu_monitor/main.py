# gpu_monitor/main.py

import fire
import logging
import time
from gpu_monitor.utils import daemonize, write_config, read_config,getGpuMemory
from gpu_monitor.email_sender import EmailSender
from gpu_monitor.config import INTERVAL

logger = logging.getLogger(__name__)

def monitor_all():
    read_config()

    @daemonize
    def monitor_alld():
        logger.info("Monitoring all GPUs in the background...")
        email_sender = EmailSender()
        while True:
            res = getGpuMemory()
            if  True in res:
                msg = f"GPUs available on the server: {[idx for idx, r in enumerate(res) if r]}"
                email_sender.send_msg(msg)
                logger.info(msg)
                return msg
            time.sleep(INTERVAL)
    
    monitor_alld()


def monitor(no: int):
    read_config()

    @daemonize
    def monitord(no: int):
        logger.info(f"Monitoring GPU {no} in the background...")
        email_sender = EmailSender()
        while True:
            res = getGpuMemory()
            if res[no]:
                msg = f"GPU {no} is now available, the program has finished running."
                email_sender.send_msg(msg)
                logger.info(msg)
                return msg
            time.sleep(INTERVAL)

    monitord(no)
    

def configure():
    from_addr = input("Please enter FROM_ADDR (your email address): ")
    smtp_passwd = input("Please enter SMTP_PASSWD (your email password): ")
    to_addr = input("Please enter TO_ADDR (recipient's email address): ")
    write_config(from_addr, smtp_passwd, to_addr)
    print("Configuration saved successfully.")

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