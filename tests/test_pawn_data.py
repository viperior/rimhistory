"""Test the extraction of pawn data from the save file"""

import extract.save


def test_get_pawn_count(config_data: dict) -> None:
    """Test counting the number of pawns identified from the save data

    Parameters:
    config_data (dict): The project configuration data as a dictionary (fixture)

    Returns:
    None
    """
    pawn_data = extract.save.Save(path_to_save_file=config_data["rimworld_save_file_path"]).pawn

    assert len(pawn_data) == 3
