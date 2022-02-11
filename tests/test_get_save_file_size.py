"""Test the get_save_file_size function"""

from save import Save


def test_get_save_file_size(config_data: dict) -> None:
    """Test the get_save_file_size function

    Parameters:
    config_data (dict): The project configuration data as a dictionary (fixture)

    Returns:
    None
    """
    file_size = Save(path_to_save_file=config_data["rimworld_save_file_path"]).data.file_size
    assert  6200000 <= file_size <= 6700000
