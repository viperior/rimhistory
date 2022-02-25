"""Test the extract_mod_list function that extracts data about installed mods from a save file"""
import json
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
    mod_list = Save(path_to_save_file=test_data_list[0]).data.dataset.mod.dictionary_list
    assert 0 < len(mod_list) < 20000
    logging.debug("List of installed mods = \n%s", json.dumps(mod_list, indent=4))

    expected_mod_attributes = ["mod_id", "mod_name", "mod_steam_id"]
    sample_mod = mod_list[0]
    logging.debug("Checking sample mod for expected attributes\nExpected attributes = %s\nSample "
                  "mod:\n%s", expected_mod_attributes, json.dumps(sample_mod, indent=4))

    for attribute in expected_mod_attributes:
        assert attribute in sample_mod.keys()

    for key in sample_mod.keys():
        assert key in expected_mod_attributes
