import json
import jsonschema as schema
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from loguru import logger
import warnings
import sys
import os
import pathlib
import contextlib
import requests
# Initialize logger once
log_file = os.path.join(pathlib.Path.cwd(), "logs", "main.log")
logger.remove()  # Clear default handlers
logger.add(sink=log_file, encoding="utf8", level="DEBUG", colorize=True)
logger.add(sys.stdout, level="INFO", colorize=True)

# Cache the schema at module load to avoid repeated file reads
# Global variable to store the cached schema
SUPPORT_MAIL_SCHEMA = None

def load_schema(schema_path="src/app/support_mail.schema.json", schema_url="https://learnosity.b-cdn.net/schema/support_mail.schema.json") -> dict:
    """
    Load and cache the JSON schema at the module level.

    Args:
        schema_path (str): Path to the schema file.

    Returns:
        dict: The loaded JSON schema.
    """
    global SUPPORT_MAIL_SCHEMA  # Ensure access to the module-level variable

    if SUPPORT_MAIL_SCHEMA is None:
        try:
            with open(schema_path, "r") as schema_file:
                SUPPORT_MAIL_SCHEMA = json.load(schema_file)
                logger.info("JSON schema successfully loaded and cached.")
        except FileNotFoundError:
            logger.warning(f"Schema file not found at {schema_path}. Attempting to load Validation Schema from {schema_url}")
            web_hosted_schema = requests.get(url=schema_url)
            SUPPORT_MAIL_SCHEMA = json.loads(web_hosted_schema.content.decode())
        except json.JSONDecodeError as e:
            logger.error(f"Schema file contains invalid JSON: {e}")
            SUPPORT_MAIL_SCHEMA = {}

    return SUPPORT_MAIL_SCHEMA



def valid_JSON_input(instance: dict, valid_schema=load_schema()) -> bool:
    """
    Validate a JSON input against a schema.

    Args:
        instance (dict): The JSON input to validate.
        valid_schema (dict): The schema to validate against. Defaults to SUPPORT_MAIL_SCHEMA.

    Returns:
        bool: True if the input is valid, False otherwise.
    """
    if valid_schema is None:
        logger.error("Validation schema is not loaded. Cannot validate input.")
        return False

    logger.info("Validating JSON input against the schema.")
    try:
        validate(instance=instance, schema=valid_schema)
        logger.success("JSON input is valid.")
        return True
    except ValidationError as e:
        logger.error(f"Validation failed: {e.message}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}")
        return False


class StreamToLogger:
    """
    Redirects streams like stdout or stderr to Loguru logger.
    """
    def __init__(self, level="INFO"):
        self._level = level

    def write(self, buffer):
        lines = buffer.rstrip().splitlines()
        for line in lines:
            logger.opt(depth=1).log(self._level, line.rstrip())

    def flush(self):
        # No need to flush, as logging handles this internally.
        pass


# Stream warnings and other messages to logger
def log_warning(message, category, filename, lineno, file=None, line=None):
    logger.warning(f"{filename}:{lineno}: {category.__name__}: {message}")


warnings.filterwarnings(action="ignore", message=r"w+")
warnings.showwarning = log_warning

# Redirect warnings to logger
stream = StreamToLogger()


def clear_logs():
    """
    Clear the contents of the log file.
    """
    try:
        with open(log_file, 'w') as log:
            log.truncate(0)
        logger.info("Logs cleared successfully.")
    except Exception as e:
        logger.error(f"Failed to clear logs: {e}")