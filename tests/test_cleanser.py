#!/usr/bin/env python
"""
   A collection of unit tests for the cleanser.py program.

Usage:
   python test_cleanser.py

Author:
   Alan Verdugo (alan.verdugo.munoz1@ibm.com)

Creation date:
   2022-01-29

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

# Unit testing.
import unittest
from unittest.mock import patch, Mock

# Log Handling.
import logging

# Module for temp files.
import tempfile

# System and OS related functionality.
import os

from json import JSONDecodeError

# Module to be tested.
#from cleanser.cleanser import read_config
from cleanser import cleanser

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

LOG = logging.getLogger(__name__)


class TestUtilities(unittest.TestCase):
    """Initial class for unit test."""

    def test_remove_files(self):
        """
        Test the complete properties of remove_files.

        It will check for  a file to be deleted by its own, two files to be
        deleted in the same process and to send an invalid file that will
        create a log warning in remove_file process.
        """
        LOG.info("Starting test_remove_files")
        # Creating a set of files in disc that wont be automated deleted
        file_name1 = tempfile.mkstemp()[1]
        file_name2 = tempfile.mkstemp()[1]
        file_name3 = tempfile.mkstemp()[1]
        # Checking when a valid file is removed
        cleanser.remove_files(file_name1)
        self.assertFalse(os.path.isfile(file_name1))
        # Checking removing more than one file at once
        cleanser.remove_files(file_name2, file_name3)
        self.assertFalse(os.path.isfile(file_name2))
        self.assertFalse(os.path.isfile(file_name3))
        # Checking with an invalid file (file does not exists)
        # TODO: assert raises exception in the next line
        cleanser.remove_files('FAIL')
        # TODO: assert an exception is raised with insufficient permissions
        # to delete

    def test_read_config(self):
        """
        Test the function to open, read and parse a JSON text files.

        It will check that the file exists, is readable and the contents are
        valid JSON.
        """
        # Creating a temporary file.
        with tempfile.NamedTemporaryFile(suffix='.json') as temp_file:
            # Changing file permissions to make the file unreadable.
            os.chmod(temp_file.name, 100)

            # Checking with an unreadable file.
            with self.assertRaises(PermissionError):
                cleanser.read_config(temp_file.name)

        # Checking with an inexistent file.
        with self.assertRaises(FileNotFoundError):
            cleanser.read_config("fake_file.sql")

        # Checking with a real, readable file which is not valid JSON/YAML.
        with self.assertRaises(JSONDecodeError):
            cleanser.read_config(self.J_CONF_FILE_B)

        with self.assertRaises(ValueError):
            cleanser.read_config(self.Y_CONF_FILE)

        # Checking with a valid JSON/YML (temporary) file.
        # Get the full path of the configuration file.
        data = cleanser.read_config(self.J_CONF_FILE)
        self.assertIsInstance(data, dict)

        data = cleanser.read_config(self.J_CONF_FILE)
        self.assertIsInstance(data, dict)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=2)
