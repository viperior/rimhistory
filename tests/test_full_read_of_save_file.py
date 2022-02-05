"""Test a full read of the save file XML data"""

import extract.extract_save_data


def test_full_read_of_save_file() -> None:
    """Test a full read of the save file XML data

    Parameters:
    None

    Returns:
    None
    """
    extract.extract_save_data.extract_rimworld_save_data()
