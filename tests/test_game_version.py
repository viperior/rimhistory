"""Test the retrieval of the RimWorld base game version from the save file"""
import logging

from rimhistory.rimhistory import extract_game_version


def test_game_version():
    """Test the retrieval of the RimWorld base game version from the save file"""
    game_version = extract_game_version()
    logging.debug("Game version = %s", game_version)

    assert game_version == "1.3.3200 rev726"
