import logging

SUCCESS_LEVEL_NUM = 25

def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        # Yes, logger takes its '*args' as 'args'.
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)

# Check if the SUCCESS level has already been added to avoid adding it multiple times
if not hasattr(logging, 'SUCCESS'):
    logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")
    logging.Logger.success = success

# Initialize the logger configuration only once
if not hasattr(logging, '_logger_configured'):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%H:%M:%S')
    logging._logger_configured = True 

# Define a function to get the logger
def get_logger(name):
    return logging.getLogger(name)

# Define a function to set the global logging level
def set_global_level(level):
    logging.getLogger().setLevel(level)

# Custom Logger Class
class CustomLogger:
    def __init__(self, original_logger, log_callback=None):
        self.original_logger = original_logger
        self.log_callback = log_callback

    def info(self, message):
        self.original_logger.info(message)
        if self.log_callback:
            self.log_callback(message)

    def success(self, message):
        self.original_logger.success(message)
        if self.log_callback:
            self.log_callback(message)

# Function to set up the custom logger
def setup_custom_logger(log_callback=None):
    logger = get_logger(__name__)
    return CustomLogger(logger, log_callback)
