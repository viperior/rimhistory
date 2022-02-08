"""Pytest fixtures"""

import json
import logging

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
    logging.debug("Loading configuration data from: %s", config_file_name)

    with open(config_file_name, "r", encoding="utf_8") as config_file:
        project_config_data = json.load(config_file)

    yield project_config_data
