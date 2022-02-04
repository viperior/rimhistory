"""Test the get_save_file_size function"""

import extract.extract_save_data


def test_get_save_file_size() -> None:
    """Test the get_save_file_size function

    Parameters:
    None

    Returns:
    None
    """
    file_size = extract.extract_save_data.get_save_file_size()
    assert  6200000 <= file_size <= 6700000
