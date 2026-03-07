from config.settings import LOG_FILE
from datetime import datetime


class NLogger:
    def log(self, text, result):
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logLine = f"{time} | INPUT: {text} | RESULT: {result}\n"
            f.write(logLine)