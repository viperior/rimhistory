"""Test the retrieval of the RimWorld base game version from the save file"""
import logging

from save import Save


def test_game_version(test_data_list: list) -> None:
    """Test the retrieval of the RimWorld base game version from the save file

    Parameters:
    test_data_list (list): The list of paths to the test input data files (fixture)

    Returns:
    None
    """
    path_to_save_file = test_data_list[0]
    game_version = Save(path_to_save_file=path_to_save_file).data.game_version
    logging.debug("Game version = %s", game_version)

    assert game_version == "1.3.3200 rev726"
