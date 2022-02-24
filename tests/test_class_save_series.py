"""Test the SaveSeries class"""

import logging
import pathlib

from save import SaveSeries


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
