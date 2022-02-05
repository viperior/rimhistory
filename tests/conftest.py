"""Pytest fixtures"""

import logging
import os
import shutil

import pytest


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
