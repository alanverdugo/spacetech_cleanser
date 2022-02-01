#!/usr/bin/python
"""
Delete old files from the file system.

Author: Alan Verdugo (alan.verdugo.munoz1@ibm.com)

Creation date: 2022-01-27

Copyright 2022 IBM Corporation

SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# OS related functionality.
import os

# Log handling.
import logging

# JSON handling.
import json

# date and time handling.
from datetime import time

# Set log level.
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
LOG = logging.getLogger(__name__)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


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
        if format_ != '.json':
            raise ValueError(f'File type not supported: {format_}')
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


def check_age(file_, config: dict) -> list:
    """Build a list of files that are past their end of life."""
    # TODO: fix this
    if (time.time() - os.path.getmtime(file_)) > "MAX_AGE_OF_LAST_LOG_FILE":
        pass
        # The newest file is older than the allowed age.


def remove_files(*file_paths: list):
    """
    Delete a collection of files from the OS file system.

    :param file_paths: A list containing file path(s).
    """
    LOG.info("Removing file(s): %s", file_paths)
    for file_path in file_paths:
        try:
            os.remove(file_path)

        except FileNotFoundError as exception:
            LOG.warning("Unable to find the file %s", file_path, exc_info=True)
            raise exception
