"""Pytest fixtures"""

import glob
import pathlib

import pytest


@pytest.fixture(scope="session")
def test_data_directory() -> pathlib.Path:
    """Return the directory containing test input data

    Parameters:
    None

    Returns:
    pathlib.Path: The directory containing test input data
    """
    return pathlib.Path("test_data")


@pytest.fixture(scope="session")
def test_data_list() -> list:
    """Return the list of paths to the test input data files

    Parameters:
    None

    Returns:
    list: The list of paths to the test input data files
    """
    return glob.glob("test_data/*.rws.gz")


@pytest.fixture(scope="session")
def test_save_file_regex() -> str:
    """Return the regex pattern matching the test input data file names

    Parameters:
    None

    Returns:
    str: The regex pattern matching the test input data file names
    """
    return r"demosave\s\d{1,10}"
