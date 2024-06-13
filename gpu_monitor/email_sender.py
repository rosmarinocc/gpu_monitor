# gpu_monitor/email_sender.py

from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import sys
import logging
from gpu_monitor.utils import read_config

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        try:
            config = read_config()
            self.from_addr = config['FROM_ADDR']
            self.password = config['FROM_SMTP_PASSWD']
            self.to_addr = config['TO_ADDR']
            self.smtp_server = 'smtp.qq.com'
        except Exception as e:
            logger.error(f"Error initializing EmailSender: {e}")
            sys.exit(1)

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def send_msg(self, msg):
        try:
            msg = MIMEText(msg, 'plain', 'utf-8')
            msg['From'] = self._format_addr(f'GPU-Monitor <{self.from_addr}>')
            msg['To'] = self._format_addr(f'Recipient <{self.to_addr}>')
            msg['Subject'] = Header('Server GPUs are available!', 'utf-8').encode()
            server = smtplib.SMTP(self.smtp_server, 25)
            server.set_debuglevel(1)
            server.login(self.from_addr, self.password)
            server.sendmail(self.from_addr, [self.to_addr], msg.as_string())
            server.quit()
            logger.info("Email sent successfully.")
        except Exception as e:
            logger.error(f"Error sending email: {e}")
