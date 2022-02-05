#!/usr/bin/python
"""
Delete old files from the file system.

Author: Alan Verdugo (alan.verdugo.munoz1@ibm.com)

Creation date: 2022-01-27

usage: cleanser.py [-h] [-v] [-d]

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Print INFO, WARNING, and ERROR messages to the stdout or
                 stderr.
  -d, --debug    Print DEBUG messages to the stdout or stderr.

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

# Parse arguments.
import argparse

# Log handling.
import logging

# JSON handling.
import json

# Time handling.
import time

# Directories pattern matching.
import re

# Directory type validation.
from genericpath import isdir

# Create log object.
LOG = logging.getLogger(__name__)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def main():
    """Orchestrate the program logic."""
    # Read configuration values.
    config = read_config(os.path.join(PROJECT_DIR, "config", "config.json"))

    # Crawl the file system and try to find old files.
    old_files = search_old_files(config=config)

    # Remove the files that were deemed unnecessary.
    if old_files:
        LOG.info("Found files to delete: %s", old_files)
        remove_objects(old_files)
    else:
        LOG.info("Did not find files old enough to delete. Nothing to do.")

    # Remove lingering job directories (and their contents).
    search_old_job_directories()


def read_config(conf_file: str) -> str:
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


def search_old_files(config):
    """Crawl the file system and try to find old files."""
    old_files = []
    for directory in config["directories"]:
        LOG.info("Checking files in %s", directory["directory"])
        for file_ in os.listdir(directory["directory"]):
            absolute_file_path = f"{directory['directory']}{file_}"
            if check_age(path_=absolute_file_path,
                         max_age_days=directory["period"]):
                old_files.append(absolute_file_path)
    return old_files


def search_old_job_directories():
    """
    Search and remove obsolete job directories.

    Job directories are supposed to be deleted by the job itself, but we
    should check if they were not deleted for any reason (E.g. a power outage).

    These directories are located in /work/jobs/ and have names like JXXXXXX,
    where XXXXXX is a 6-digit integer number (E.g. J123456, J000007).
    """
    job_directories = []
    jobs_parent_dir = "/work/jobs/"
    LOG.info("Checking job directories in %s", jobs_parent_dir)

    for directory in os.listdir(jobs_parent_dir):
        # Select only the JXXXXXX directories
        if re.findall(r"^J[0-9]{6}$", directory):
            # Get the absolute paths of the directories in /work/jobs/
            directory = f"{jobs_parent_dir}{directory}"
            job_directories.append(directory)

    directories_to_delete = []
    for directory in job_directories:
        # Check if indeed this is a directory, and if it is past its EOL.
        if isdir(directory) and check_age(path_=directory, max_age_days=30):
            directories_to_delete.append(directory)

    if directories_to_delete:
        LOG.info("Found job directories to delete: %s", directories_to_delete)
        remove_objects(directories_to_delete)
    else:
        LOG.info("Did not find job directories old enough to delete. "
                 "Nothing to do.")


def check_age(path_: str, max_age_days: int) -> bool:
    """
    Build a list of files or directories that are past their end of life.

    :param path: The absolute path of a file or directory to check.
    :param max_age_days: The integer number of days for the allowed lifespan.
    """
    if (time.time() - os.path.getmtime(path_)) > (max_age_days * 24 * 60 * 60):
        LOG.debug("%s is old enough to be deleted.", path_)
        return True
    LOG.debug("%s is not old enough to be deleted.", path_)
    return False


def remove_objects(paths: list):
    """
    Delete a collection of files or directories from the OS file system.

    :param file_paths: A list containing file or directories absolute path(s).
    """
    LOG.info("Removing file(s) or directories: %s", paths)
    for path in paths:
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                os.rmdir(path)
        except FileNotFoundError:
            LOG.warning("Unable to find: %s", path)
        except PermissionError:
            LOG.error("Unable to delete due to lack of permissions: %s", path)


def get_args():
    """Get and parse arguments."""
    parser = argparse.ArgumentParser()
    # Log level parameters.
    parser.add_argument("-v", "--verbose",
                        help="Print INFO, WARNING, and ERROR messages "
                        "to the stdout or stderr.",
                        dest="verbose",
                        default=False,
                        action="store_true")
    parser.add_argument("-d", "--debug",
                        help="Print DEBUG messages to the stdout or stderr.",
                        dest="debug",
                        default=False,
                        action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    # Parse arguments from the CLI.
    args = get_args()

    if args.debug:
        LOG.setLevel(logging.DEBUG)
    elif args.verbose:
        LOG.setLevel(logging.INFO)
    else:
        LOG.setLevel(logging.ERROR)

    # Stream handler for human consumption and stderr.
    STREAM_HANDLER = logging.StreamHandler()
    STREAM_FORMATTER = logging.Formatter("%(asctime)s - "
                                         "%(levelname)s - "
                                         "%(message)s")

    STREAM_HANDLER.setFormatter(STREAM_FORMATTER)
    LOG.addHandler(STREAM_HANDLER)

    main()
