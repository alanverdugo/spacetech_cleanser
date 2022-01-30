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

# Log Handling.
import logging

# Module for temporary files.
import tempfile

# System and OS related functionality.
import os

import json

# Module to be tested.
from cleanser import cleanser

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

LOG = logging.getLogger(__name__)


class TestCleanser(unittest.TestCase):
    """Initial class for unit test."""

    def test_remove_files(self):
        """
        Test the complete properties of remove_files.

        It will check for  a file to be deleted by its own, two files to be
        deleted in the same process and to send an invalid file that will
        create a log warning in remove_file process.
        """
        LOG.info("Starting test_remove_files")
        # Happy path. Checking when a valid file is removed.
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file0:
            file_name = temp_file0.name
            self.assertTrue(os.path.exists(file_name))
            cleanser.remove_files(file_name)
            self.assertFalse(os.path.exists(file_name))

        # Testing failed deletion of an inexistent file.
        with self.assertRaises(FileNotFoundError):
            cleanser.remove_files('fake_file.json')

    def test_read_config(self):
        """
        Test the function to open, read and parse a JSON text files.

        It will check that the file exists, is readable and the contents are
        valid JSON.
        """
        # Checking with an unreadable file.
        with tempfile.NamedTemporaryFile(suffix='.json') as temp_file:
            # Changing file permissions to make the file unreadable.
            os.chmod(temp_file.name, 100)

            with self.assertRaises(PermissionError):
                cleanser.read_config(temp_file.name)

        # Checking with an inexistent file.
        with self.assertRaises(FileNotFoundError):
            cleanser.read_config("fake_file.json")

        # Checking with an unsupported file extension.
        with self.assertRaises(ValueError):
            cleanser.read_config(os.path.abspath(__file__))

        # Checking with a valid JSON file.
        data = cleanser.read_config(os.path.join(PROJECT_DIR, "config", "config.json"))
        self.assertIsInstance(data, dict)

        # Checking with a valid file that has invalid JSON formatting.
        with tempfile.NamedTemporaryFile(suffix='.json') as temp_file:
            # Inserting invalid data into the JSON file.
            temp_file.write(b'I am invalid JSON data!')

            with self.assertRaises(json.JSONDecodeError):
                cleanser.read_config(temp_file.name)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=2)
