"""Test the get_save_file_size function"""

from save import Save


def test_get_save_file_size(test_data_list: list) -> None:
    """Test the get_save_file_size function

    Parameters:
    test_data_list (list): The list of paths to the test input data files (fixture)

    Returns:
    None
    """
    file_size = Save(path_to_save_file=test_data_list[0]).data.file_size
    assert 2000000 <= file_size <= 3000000
