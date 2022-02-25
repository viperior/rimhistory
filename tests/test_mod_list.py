"""Test the extract_mod_list function that extracts data about installed mods from a save file"""
import logging

from save import Save


def test_mod_list(test_data_list: list) -> None:
    """Test the extract_mod_list function that extracts data about installed mods from a save
    file

    Parameters:
    test_data_list (list): The list of paths to the test input data files (fixture)

    Returns:
    None
    """
    mod_df = Save(path_to_save_file=test_data_list[0]).data.mod
    assert 0 < len(mod_df.index) < 20000
    logging.debug("List of installed mods = \n%s", mod_df)

    expected_mod_attributes = [
        "mod_id",
        "mod_name",
        "mod_steam_id",
        "time_ticks",
    ]
    sample_mod = mod_df.head(1)
    logging.debug("Checking sample mod for expected attributes\nExpected attributes = %s\nSample "
                  "mod:\n%s", expected_mod_attributes, sample_mod)

    for attribute in expected_mod_attributes:
        assert attribute in sample_mod.keys()

    for key in sample_mod.keys():
        assert key in expected_mod_attributes
