"""Test the extraction of pawn environment ambient temperature"""

import logging

from save import Save


def test_pawn_ambient_temperature(test_data_list: list) -> None:
    """Test the extraction of pawn environment ambient temperature

    Parameters:
    test_data_list (list): The list of paths to the test input data files (fixture)

    Returns:
    None
    """
    pawn_df = Save(path_to_save_file=test_data_list[0]).data.pawn
    logging.debug("Sample pawn data =\n%s", pawn_df.head(5))

    assert "pawn_ambient_temperature" in pawn_df.columns
