"""Test the plant_dataframe function"""

import logging

import pandas

import extract.extract_save_data


def test_plant_dataframe() -> None:
    """Test the plant_dataframe function

    Parameters:
    None

    Returns:
    None
    """
    plant_dataframe = extract.extract_save_data.plant_dataframe()

    # Test the data type of the frame
    logging.debug("type(plant_dataframe) = %s", type(plant_dataframe))
    assert isinstance(plant_dataframe, pandas.core.frame.DataFrame)

    # Test the expected columns
    expected_columns = [
        "plant_id",
        "plant_definition",
        "plant_map_id",
        "plant_position",
        "plant_growth",
        "plant_age"
    ]
    logging.debug("Expected columns (count = %d) = %s", len(expected_columns), expected_columns)
    logging.debug("Actual columns (count = %d) = %s", len(plant_dataframe.columns),
        plant_dataframe.columns)
    assert len(plant_dataframe.columns) == len(expected_columns)

    for column in expected_columns:
        assert column in plant_dataframe.columns

    # Test the expected number of rows
    row_count_minimum = 10000
    row_count_maximum = 40000
    logging.debug("Expected rows in dataframe is between %d and %d", row_count_minimum,
        row_count_maximum)
    logging.debug("Actual rows in dataframe = %d", len(plant_dataframe.index))
    assert row_count_minimum <= len(plant_dataframe.index) <= row_count_maximum
