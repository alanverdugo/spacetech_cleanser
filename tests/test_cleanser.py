#!/usr/bin/env python
"""
   A collection of unit tests for the cleanser.py program.

Usage:
   python test_cleanser.py

Author:
   Alan Verdugo (alan.verdugo.munoz1@ibm.com)

Creation date:
   2022-01-29
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
from ..cleanser.cleanser import read_config


PARENT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

LOG = logging.getLogger(__name__)


class TestUtilities(unittest.TestCase):
    """Initial class for unit test."""

    # Configuration file.
    J_CONF_FILE = os.path.join(PARENT_DIR, 'tests', 'conf', 'config_values.json')
    J_CONF_FILE_B = os.path.join(PARENT_DIR, 'tests', 'conf', 'BAD_config_values.json')
    Y_CONF_FILE = os.path.join(PARENT_DIR, 'tests', 'conf', 'config_values.yaml')

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
        generic.remove_files(file_name1)
        self.assertFalse(os.path.isfile(file_name1))
        # Checking removing more than one file at once
        generic.remove_files(file_name2, file_name3)
        self.assertFalse(os.path.isfile(file_name2))
        self.assertFalse(os.path.isfile(file_name3))
        # Checking with an invalid file (file does not exists)
        generic.remove_files('FAIL')

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
                generic.read_config(temp_file.name)

        # Checking with an inexistent file.
        with self.assertRaises(FileNotFoundError):
            generic.read_config("fake_file.sql")

        # Checking with a real, readable file which is not valid JSON/YAML.
        with self.assertRaises(JSONDecodeError):
            generic.read_config(self.J_CONF_FILE_B)

        with self.assertRaises(ValueError):
            generic.read_config(self.Y_CONF_FILE)

        # Checking with a valid JSON/YML (temporary) file.
        # Get the full path of the configuration file.
        data = generic.read_config(self.J_CONF_FILE)
        self.assertIsInstance(data, dict)

        data = generic.read_config(self.J_CONF_FILE)
        self.assertIsInstance(data, dict)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=2)
