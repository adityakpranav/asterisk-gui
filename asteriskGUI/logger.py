import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from config import SERVER_DIR, TOKEN_USER, FILTER_URLS
# Create logs directory if it doesn't exist

LOG_DIR = os.path.join("/home/exch/asteriskGUI","Logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "api.log")

MAX_BYTES = 50 * 1024  # 50 KB limit per file
BACKUP_COUNT = 20      # Keeps the 20 most recent timestamped log files


class TimestampedRotatingFileHandler(RotatingFileHandler):
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        # Create a timestamped filename (e.g., logs/api_2026-11-19_15-41-30.log)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_dir = os.path.dirname(self.baseFilename)
        archived_file = os.path.join(base_dir, f"api_{timestamp}.log")

        # Handle edge case if multiple rollovers happen within the same second
        counter = 1
        while os.path.exists(archived_file):
            archived_file = os.path.join(base_dir, f"api_{timestamp}_{counter}.log")
            counter += 1

        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, archived_file)

        # Clean up oldest archived logs if backupCount is exceeded
        if self.backupCount > 0:
            archived_logs = sorted(
                [
                    os.path.join(base_dir, f)
                    for f in os.listdir(base_dir)
                    if f.startswith("api_") and f.endswith(".log")
                ],
                key=os.path.getmtime,
            )
            while len(archived_logs) > self.backupCount:
                os.remove(archived_logs.pop(0))

        # Open a fresh active api.log file
        if not self.delay:
            self.stream = self._open()


def setup_logger(name: str = "api_logger") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = TimestampedRotatingFileHandler(
            LOG_FILE,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

def log_info(payload,request):

    if (request.url.path not in FILTER_URLS):
        client_ip = getattr(request.state, "client_ip", "Unknown")
        session_token = request.cookies.get("session_auth_token",None)
        user = TOKEN_USER.get(session_token,None)
        
        logger.info(f"AMI A Triggered | IP: {client_ip} | User : {user} | Command: {payload.command}")
        

logger = setup_logger()