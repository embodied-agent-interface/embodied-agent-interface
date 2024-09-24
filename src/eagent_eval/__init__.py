import logging
import os
import yaml
# Configure logging
logger = logging.getLogger(__name__)

__version__ = "1.0"

# Load global configuration
config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "global_config.yaml")
logger.debug(f"Loading configuration from {config_path}")
try:
    with open(config_path) as f:
        global_config = yaml.load(f, Loader=yaml.FullLoader)
        logger.debug(f"Loaded global configuration: {global_config}")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise

# Override paths from environment variables if set
helm_output_path = os.environ.get("HELM_OUTPUT_PATH", global_config.get("helm_output_path"))
helm_output_path = os.path.expanduser(helm_output_path)
logger.debug(f"helm_output_path: {helm_output_path}")



root_path = os.path.dirname(os.path.realpath(__file__))

if not os.path.isabs(helm_output_path):
    helm_output_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), helm_output_path)
