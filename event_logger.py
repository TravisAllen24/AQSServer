import logging
import os

# 1. Define the directory and log file name

def get_logger(name, file_name, level=logging.DEBUG):
    log_dir = "logs"
    log_file = os.path.join(log_dir, file_name)

    # 2. Automatically create the folder if it does not exist
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger