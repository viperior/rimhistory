"""Test the extract_mod_list function that extracta data about installed mods from a save file"""
import json
import logging

import extract.save


def test_mod_list(config_data: dict) -> None:
    """Test the extract_mod_list function that extracts data about installed mods from a save
    file

    Parameters:
    config_data (dict): The project configuration data as a dictionary (fixture)

    Returns:
    None
    """
    path_to_save_file = config_data["rimworld_save_file_path"]
    mod_list = extract.save.Save(path_to_save_file=path_to_save_file).mod["dictionary_list"]
    assert 0 < len(mod_list) < 20000
    logging.debug("List of installed mods = \n%s", json.dumps(mod_list, indent=4))

    expected_mod_attributes = ["mod_id", "mod_name", "mod_steam_id"]
    sample_mod = mod_list[0]
    logging.debug("Checking sample mod for expected attributes\nExpected attributes = %s\nSample "\
        "mod:\n%s", expected_mod_attributes, json.dumps(sample_mod, indent=4))

    for attribute in expected_mod_attributes:
        assert attribute in sample_mod.keys()

    for key in sample_mod.keys():
        assert key in expected_mod_attributes
