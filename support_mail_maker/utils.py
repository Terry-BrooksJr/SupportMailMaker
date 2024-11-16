import jsonschema as schema
from jsonschema.exceptions import ValidationError
import json
from loguru import logger
import warnings
import sys
import os
import pathlib
import contextlib


support_mail_content_schema = {}
with open('support_mail_maker/supportmail.schema.json', 'r') as schema_spec:
    support_mail_content_schema = json.load(schema_spec)


def valid_JSON_input(instance:dict, schema=support_mail_content_schema):
    logger.info('Received Request To Validate JSON Input Against SupportMail JSON Schema')
    try:
        schema.validate(instance)
        logger.success('Input is Valid.')
        return True
    except ValidationError as e:
        logger.error(f'ERROR: Invalid Schema. Details: {str(e)}')



class StreamToLogger:

    def __init__(self, level="INFO"):
        self._level = level

    def write(self, buffer):
        for line in buffer.rstrip().splitlines():
            logger.opt(depth=1).log(self._level, line.rstrip())

    def flush(self):
        pass

logger.remove()
logger.add(sys.__stdout__)

stream = StreamToLogger()
with contextlib.redirect_stdout(stream):
    print("Standard output is sent to added handlers.")

log_file = os.path.join(pathlib.Path.cwd(), 'logs', 'main.log')
def log_warning(message, category, filename, lineno, file=None, line=None):
    logger.warning(f" {message}")
warnings.filterwarnings(action='ignore', message=r"w+")
warnings.showwarning = log_warning

logger.add(sink=sys.stderr, level="WARNING", colorize=True)
logger.add(sink=log_file, encoding="utf8", level="DEBUG", colorize=True)
logger.add(sink=sys.stdout, level="INFO", colorize=True)