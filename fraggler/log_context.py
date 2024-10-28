# context_logger.py
import logging
import contextvars

# Create a ContextVar to hold the logger instance
class Logger:
    _instance = None

    @staticmethod
    def get_logger():
        if Logger._instance is None:
            Logger._instance = logging.getLogger("fraggler")
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            Logger._instance.addHandler(handler)
            Logger._instance.setLevel(logging.INFO)
        return Logger._instance
