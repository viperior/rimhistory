"""Test the extraction of pawn data from the save file"""

import extract.extract_save_data


def test_get_pawn_count() -> None:
    """Test counting the number of pawns identified from the save data

    Parameters:
    file_path (str): The path to the save game file
    expected (int): The number of expected pawns to find in the corresponding save data

    Returns:
    None
    """
    assert extract.extract_save_data.get_pawn_count() == 3
