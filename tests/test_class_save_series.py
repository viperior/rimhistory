"""Test the SaveSeries class"""

import logging
import pathlib
import random
import string
import shutil

import pytest

from save import Save
from save import SaveSeries


def get_test_input_data_sample_save_files() -> list:
    """Return test input data for the test_scan_save_file_dir function

    Parameters:
    None

    Returns:
    list: A list of tuples containing test input metadata (file_name_list, regex_pattern,
    expected_match_count)
    """
    sample_valid_save_label = "mysave"
    sample_regex_pattern = f"{sample_valid_save_label}\\s\\d{{1,10}}"
    valid_save_list_with_leading_zeroes = [
        f"{sample_valid_save_label} 00{index + 1}.rws" for index in range(3)
    ]
    logging.debug("valid_save_list_with_leading_zeroes = %s", valid_save_list_with_leading_zeroes)
    valid_save_list_sans_leading_zeroes = [
        f"{sample_valid_save_label} {index + 1}.rws" for index in range(3)
    ]
    logging.debug("valid_save_list_sans_leading_zeroes = %s", valid_save_list_sans_leading_zeroes)
    junk_file_names = [
        f"{''.join(random.choices(string.ascii_lowercase, k=10))}.rws" for _ in range(3)
    ]
    logging.debug("junk_file_names = %s", junk_file_names)
    test_input_data = [
        (valid_save_list_sans_leading_zeroes, sample_regex_pattern, 3),
        (valid_save_list_with_leading_zeroes, sample_regex_pattern, 3),
        (valid_save_list_sans_leading_zeroes + junk_file_names, sample_regex_pattern, 3),
        (valid_save_list_with_leading_zeroes + junk_file_names, sample_regex_pattern, 3),
    ]
    logging.debug("test_input_data = %s", test_input_data)

    return test_input_data


def test_aggregate_dataframes(tmp_path: pathlib.Path) -> None:
    """Test the SaveSeries.test_aggregate_dataframes function by validating combined row counts

    Parameters:
    tmp_path (pathlib.Path): The path used to stage files needed for testing (fixture)

    Returns:
    None
    """
    test_file_count = 3
    test_file_path_list = [tmp_path / f"mysave {index + 1}.rws" for index in range(test_file_count)]
    sample_save_file_path = "data/sample_rimworld_save.rws"

    for file_path in test_file_path_list:
        shutil.copyfile(src=sample_save_file_path, dst=file_path)

    series = SaveSeries(save_dir_path=tmp_path, save_file_regex_pattern=r"mysave\s\d{1,10}")
    sample_save = Save(path_to_save_file=sample_save_file_path)
    single_plant_dataframe = sample_save.data.dataset.plant.dataframe
    expected_count = len(single_plant_dataframe.index) * test_file_count
    actual_count = len(series.dataset.plant.dataframe.index)
    logging.debug("Dataframe aggregation test result:\nExpected count: %d\nActual count: %d",
                  expected_count, actual_count)

    assert actual_count == expected_count


@pytest.mark.parametrize(
    "file_name_list, regex_pattern, expected_match_count",
    get_test_input_data_sample_save_files()
)
def test_scan_save_file_dir(file_name_list: list, regex_pattern: str, expected_match_count: int,
                            tmp_path: pathlib.Path) -> None:
    """Test the scan_save_file_dir function of the SaveSeries class

    Parameters:
    file_name_list (list): The list of file names to test
    regex_pattern (str): The regex pattern to match against the file names
    expected_match_count (int): The number of expected matching files in file_name_list
    tmp_path (pathlib.Path): The path used to stage files needed for testing (fixture)

    Returns:
    None
    """
    for save_file_name in file_name_list:
        shutil.copyfile(src="data/sample_rimworld_save.rws", dst=tmp_path / save_file_name)

    series = SaveSeries(
        save_dir_path=tmp_path,
        save_file_regex_pattern=regex_pattern
    )

    # Test the SaveSeries object type
    assert isinstance(series, SaveSeries)

    # Test whether the dictionary property was populated
    for save_base_name in series.dictionary:
        logging.debug("Save base name = %s", save_base_name)

    assert isinstance(series.dictionary, dict)
    assert 1 <= len(series.dictionary) <= 100
    assert len(series.dictionary) == expected_match_count

    # Test a specific property in one of the processed Save objects
    sample_save_key = list(series.dictionary.keys())[2]
    sample_game_version = series.dictionary[sample_save_key]["save"].data.game_version
    logging.debug("Sample property from one of the processed save files = game_version = %s",
                  sample_game_version)
    assert isinstance(sample_game_version, str)
    assert sample_game_version == "1.3.3200 rev726"
