import jsonschema as schema
from jsonschema.exceptions import ValidationError
import json
from loguru import logger
import warnings
import sys
import os
import pathlib
import contextlib
import tempfile


support_mail_content_schema = {}
schema_temp = tempfile.TemporaryFile
with open('support_mail_maker/support_mail.schema.json', 'r') as schema_spec:
    support_mail_content_schema = json.load(schema_spec)


def valid_JSON_input(instance:dict, schema=support_mail_content_schema):
    logger.info('Received Request To Validate JSON Input Against SupportMail JSON Schema')
    try:
        schema.validate(instance)
        logger.success('Input is Valid.')
        return True
    except ValidationError as e:
        logger.error(f'ERROR: Invalid Schema. Details: {str(e)}')
    except Exception as e:
        logger.error(f'ERROR: Unexpected Error. Details: {str(e)}')



class StreamToLogger:

    def __init__(self, level="DEBUG"):
        self._level = level

    def write(self, buffer):
        for line in buffer.rstrip().splitlines():
            logger.opt(depth=1).log(self._level, line.rstrip())

    def flush(self):
        pass
log_file = os.path.join(pathlib.Path.cwd(), 'logs', 'main.log')
logger.remove()

def log_warning(message, category, filename, lineno, file=None, line=None):
    logger.warning(f" {message}")
warnings.filterwarnings(action='ignore', message=r"w+")
warnings.showwarning = log_warning
stream = StreamToLogger()
logger.add(sink=log_file, encoding="utf8", level="DEBUG", colorize=True)

with contextlib.redirect_stdout(stream):
    print("Standard output is sent to added handlers.")



