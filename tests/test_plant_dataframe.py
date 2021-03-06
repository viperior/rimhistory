"""Test the plant_dataframe function"""

import logging

import pandas

from save import Save


def test_plant_dataframe(test_data_list: list) -> None:
    """Test the plant_dataframe function

    Parameters:
    test_data_list (list): The list of paths to the test input data files (fixture)

    Returns:
    None
    """
    save = Save(path_to_save_file=test_data_list[0])
    plant_df = save.data.plant

    # Test the data type of the frame
    assert isinstance(plant_df, pandas.core.frame.DataFrame)

    # Test the expected columns
    expected_columns = [
        "plant_id",
        "plant_definition",
        "plant_map_id",
        "plant_position",
        "plant_growth",
        "plant_growth_bin",
        "plant_growth_percentage",
        "plant_age",
        "time_ticks",
    ]
    logging.debug("Expected columns (count = %d) = %s", len(expected_columns), expected_columns)
    logging.debug("Actual columns (count = %d) = %s", len(plant_df.columns), plant_df.columns)
    assert len(plant_df.columns) == len(expected_columns)

    for column in expected_columns:
        assert column in plant_df.columns

    # Test the expected number of rows
    row_count_minimum = 10000
    row_count_maximum = 40000
    logging.debug("Expected rows in dataframe is between %d and %d", row_count_minimum,
                  row_count_maximum)
    logging.debug("Actual rows in dataframe = %d", len(plant_df.index))
    assert row_count_minimum <= len(plant_df.index) <= row_count_maximum
