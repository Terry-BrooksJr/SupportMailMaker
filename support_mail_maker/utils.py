import jsonschema as schema
from jsonschema import validate

from jsonschema.exceptions import ValidationError
import json
from loguru import logger
import warnings
import sys
import os
import pathlib
import contextlib

logger.remove(0)
support_mail_content_schema = {}
with open("support_mail_maker/support_mail.schema.json", "r") as schema_spec:
    support_mail_content_schema = json.load(schema_spec)


def valid_JSON_input(instance: dict, valid_schema=support_mail_content_schema):
    logger.info(
        "Received Request To Validate JSON Input Against SupportMail JSON Schema"
    )
    try:
        validate(instance=instance, schema=valid_schema)
        logger.success("Input is Valid.")
        return True
    except ValidationError as e:
        logger.error(f"ERROR: Invalid Schema. Details: {str(e)}")
        raise ValidationError(f"ERROR: Invalid Schema. Details: {str(e)}") from e
    except Exception as e:
        logger.error(f"ERROR: Unexpected Error. Details: {str(e)}")


class StreamToLogger:

    def __init__(self, level="DEBUG"):
        self._level = level

    def write(self, buffer):
        for line in buffer.rstrip().splitlines():
            logger.opt(depth=1).log(self._level, line.rstrip())

    def flush(self):
        pass


log_file = os.path.join(pathlib.Path.cwd(), "logs", "main.log")
logger.remove()


def log_warning(message, category, filename, lineno, file=None, line=None):
    logger.warning(f" {message}")

logger.add(sink=log_file, encoding="utf8", level="DEBUG", colorize=True)
logger.add(sys.stdout, level="DEBUG", colorize=True)

warnings.filterwarnings(action="ignore", message=r"w+")
warnings.showwarning = log_warning
stream = StreamToLogger()

# with contextlib.redirect_stdout(stream):
#     print("Standard output is sent to added handlers.")
