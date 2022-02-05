"""Pytest fixtures"""

import json
import logging
import os
import shutil

import pytest


@pytest.fixture(scope="session")
def config_data() -> dict:
    """Return the project configuration data as a dictionary

    Parameters:
    None

    Returns:
    dict: Dictionary containing project configuration settings
    """
    config_file_name = "config.json"
    logging.debug("Loading configuration data from: %s")

    with open(config_file_name, "r", encoding="utf_8") as config_file:
        project_config_data = json.load(config_file)

    yield project_config_data


@pytest.fixture(scope="session")
def test_data_directory() -> str:
    """Return the path to the temporary directory where test artifacts are stored

    Parameters:
    None

    Returns:
    str: The path to the temporary test data directory
    """
    test_directory = "tmpdir"
    subdirectory_list = ["data", "reports"]

    if not os.path.isdir(test_directory):
        logging.debug("Setting up test data directory: %s", test_directory)
        os.mkdir(test_directory)

        for subdirectory in subdirectory_list:
            if not os.path.isdir(subdirectory):
                os.mkdir(f"{test_directory}/{subdirectory}")

    yield test_directory

    logging.debug("Cleaning up test data directory: %s", test_directory)
    shutil.rmtree(test_directory)
