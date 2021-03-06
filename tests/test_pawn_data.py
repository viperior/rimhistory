"""Test the extraction of pawn data from the save file"""

from save import Save


def test_get_pawn_count(test_data_list: list) -> None:
    """Test counting the number of pawns identified from the save data

    Parameters:
    test_data_list (list): The list of paths to the test input data files (fixture)

    Returns:
    None
    """
    pawn_df = Save(path_to_save_file=test_data_list[0]).data.pawn
    pawn_df.query("current_record == True", inplace=True)

    assert len(pawn_df.index) == 5
