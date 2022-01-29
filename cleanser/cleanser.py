#!/usr/bin/python
"""
Delete old files from the file system.

An old file is 

Author:
Alan Verdugo (alan.verdugo.munoz1@ibm.com)

Creation date:
2022-01-27
"""

# OS related functionality.
import os

# Log handling.
import logging

# JSON handling.
import json


# Set log level.
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
LOG = logging.getLogger(__name__)


def main():
    """Orchestrate the program logic."""

    # Read configuration values.
    conf = read_config(os.path.join(PROJECT_DIR, "conf", "config.json"))


def read_config(conf_file: str) -> dict:
    """
    Load configuration/environment files.

    :param conf_file: Path to configuration file.
    :return: Dictionary containing the JSON configuration.
    """
    format_ = os.path.splitext(conf_file)[-1]
    try:
        if format_ is not '.json':
            raise ValueError('File type not supported.')
        with open(file=conf_file, mode='r', encoding='utf-8') as file_:
            config = file_.read()
            config = json.loads(config)
    except FileNotFoundError as exception:
        LOG.error("File not found %s", conf_file, exc_info=True)
        raise exception
    except PermissionError as exception:
        LOG.error("Unable to read file %s", conf_file, exc_info=True)
        raise exception
    except json.JSONDecodeError as exception:
        LOG.error('Invalid JSON format in file: %s', conf_file, exc_info=True)
        raise exception
    except ValueError as exception:
        LOG.error("File not supported.", exc_info=True)
        raise exception
    else:
        LOG.info('[%s] file loaded. %s', format_, conf_file)
        return config


def check_age(file_ : , config: dict) -> list:
    """Build a list of files that are past their end of life."""
    if ((time.time() - os.path.getmtime(file_)) >
        MAX_AGE_OF_LAST_LOG_FILE):
        # The newest file is older than 10 minutes.


def clean_old_files(files: list):
    """Delete the files that are no longer needed."""
    for file_ in files:
