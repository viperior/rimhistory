"""Test the retrieval of the RimWorld base game version from the save file"""
import logging

from save import Save


def test_game_version(config_data: dict) -> None:
    """Test the retrieval of the RimWorld base game version from the save file

    Parameters:
    config_data (dict): The project configuration data as a dictionary (fixture)

    Returns:
    None
    """
    path_to_save_file = config_data["rimworld_save_file_path"]
    game_version = Save(path_to_save_file=path_to_save_file).data.game_version
    logging.debug("Game version = %s", game_version)

    assert game_version == "1.3.3200 rev726"
