"""Test the retrieval of the RimWorld base game version from the save file"""
import logging

import extract.extract_save_data


def test_game_version():
    """Test the retrieval of the RimWorld base game version from the save file"""
    game_version = extract.extract_save_data.extract_game_version()
    logging.debug("Game version = %s", game_version)

    assert game_version == "1.3.3200 rev726"
