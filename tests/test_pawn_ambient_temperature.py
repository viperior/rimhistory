"""Test the extraction of pawn environment ambient temperature"""

import logging

import extract.extract_save_data


def test_pawn_ambient_temperature() -> None:
    """Test the extraction of pawn environment ambient temperature

    Parameters:
    None

    Returns:
    None
    """
    pawn_data = extract.extract_save_data.get_pawn_data()
    logging.debug(pawn_data[0].keys())

    assert "pawn_ambient_temperature" in pawn_data[0].keys()
