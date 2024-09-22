import logging
import os
from datetime import datetime


def setup_logging(log_dir="logs", function_name=None):
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = (
        f"app_{timestamp}.log"
        if function_name is None
        else f"{function_name}_{timestamp}.log"
    )
    log_file = os.path.join(log_dir, file_name)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    print(
        f"Log file for {function_name if function_name else 'main'}: {os.path.abspath(log_file)}"
    )
    return log_file