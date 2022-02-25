"""Test the SaveSeries class"""

import logging
import pathlib

from save import Save
from save import SaveSeries


def test_bad_regex(test_data_directory: pathlib.Path) -> None:
    """Test the SaveSeries class using a regex pattern matching 0 save files

    Parameters:
    test_data_directory (pathlib.Path): The directory containing test input data (fixture)

    Returns:
    None
    """
    series = None

    try:
        series = SaveSeries(save_dir_path=test_data_directory,
                            save_file_regex_pattern="no_file_matches_this")
    except AssertionError as error:
        assert isinstance(error, AssertionError)
    finally:
        assert series is None


def test_class_save_series(test_data_directory: pathlib.Path, test_save_file_regex: str) -> None:
    """Test the SaveSeries class

    Parameters:
    test_data_directory (pathlib.Path): The directory containing test input data (fixture)
    test_save_file_regex (str): The regex pattern matching the test input data file names (fixture)

    Returns:
    None
    """
    series = SaveSeries(save_dir_path=test_data_directory,
                        save_file_regex_pattern=test_save_file_regex)
    expected_count = 24232
    actual_count = len(series.dataset.plant.dataframe.index)
    logging.debug("Dataframe aggregation test result:\nExpected count: %d\nActual count: %d",
                  expected_count, actual_count)

    assert actual_count == expected_count


def test_empty_source_directory(tmp_path: pathlib.Path, test_save_file_regex: str) -> None:
    """Test the SaveSeries class by attempting to load a series of saves from an empty directory

    Parameters:
    tmp_path (pathlib.Path): The path used to stage files needed for testing (fixture)
    test_save_file_regex (str): The regex pattern matching the test input data file names (fixture)

    Returns:
    None
    """
    series = None

    try:
        series = SaveSeries(save_dir_path=tmp_path, save_file_regex_pattern=test_save_file_regex)
    except AssertionError as error:
        assert isinstance(error, AssertionError)
    finally:
        assert series is None


def test_load_save_data_worker_task(test_data_directory: pathlib.Path, test_save_file_regex: str)\
    -> None:
    """Test the SaveSeries.load_save_data_worker_task function

    Parameters:
    test_data_directory (pathlib.Path): The directory containing test input data (fixture)
    test_save_file_regex (str): The regex pattern matching the test input data file names (fixture)

    Return:
    None
    """
    series = SaveSeries(
        save_dir_path=test_data_directory,
        save_file_regex_pattern=test_save_file_regex
    )
    test_save_base_name = "demosave 4"
    assert len(series.dictionary) == 3
    series.dictionary[test_save_base_name] = {"path": test_data_directory / "demosave 1.rws.gz"}
    save = series.load_save_data_worker_task(test_save_base_name)

    # Validate that the new save file was processed successfully
    assert isinstance(save, Save)
    assert len(series.dictionary) == 4
    assert len(save.data.dataset.plant.dataframe.index) == 11169
