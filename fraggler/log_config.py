import logging

# Configure the logger

# It should be higher than INFO (which is 20) but lower than WARNING (which is 30)
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


def format_log_message(message, mdefs, sending):
    # Retrieve the message definition based on the message type
    mdef = mdefs.get(message.mid, None)
    if not mdef:
        return "Unknown message type"
    
    # Start building the formatted string
    action = "Sending" if sending else "Receiving"
    formatted_str = f"{action} Message - Type: {mdef['name']} - "

    # Iterate over the keys and values of message.msg and add them to the formatted string
    for key, value in message.msg.items():
        if key == "Payload" or key == "DU":
            continue
        formatted_str += f"{key}: {value} "

    return formatted_str