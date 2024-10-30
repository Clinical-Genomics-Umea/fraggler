import logging

# Define a custom logging level for 'SUCCESS' messages with level number 25
SUCCESS_LEVEL_NUM = 25

def success(self, message, *args, **kws):
    """
    Log a message with severity 'SUCCESS' at SUCCESS_LEVEL_NUM (25).
    
    Parameters:
    - self: The logger instance
    - message (str): The log message to display
    - *args: Additional positional arguments for the message formatting
    - **kws: Additional keyword arguments, including those passed to `_log` method
    """
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        # Pass *args as positional arguments to the '_log' method for processing
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)

# Check if the SUCCESS level is already defined in logging to avoid re-adding it
if not hasattr(logging, 'SUCCESS'):
    # Register the custom 'SUCCESS' log level with the logging module
    logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")
    # Add the 'success' method to the Logger class
    logging.Logger.success = success

# Initialize the logger configuration if it has not already been set up
if not hasattr(logging, '_logger_configured'):
    # Configure the basic logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    # Flag to indicate that the logger has been configured
    logging._logger_configured = True

def get_logger(name):
    """
    Retrieve a logger with the specified name.

    Parameters:
    - name (str): The name for the logger, typically matching the module or application component
    
    Returns:
    - logging.Logger: A configured logger instance
    """
    return logging.getLogger(name)

def set_global_level(level):
    """
    Set the global logging level for all loggers in the application.

    Parameters:
    - level (int): The logging level to set, e.g., logging.DEBUG, logging.INFO, etc.
    """
    logging.getLogger().setLevel(level)
