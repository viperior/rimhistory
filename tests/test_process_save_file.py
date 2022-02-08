"""Test the extract.modify_save_file.process_save_file function"""

import json
import xml.etree.ElementTree

import extract.modify_save_file


def test_process_save_file(config_data: dict, tmp_path) -> None:
    """Test the extract.modify_save_file.process_save_file function

    Parameters:
    config_data (dict): The project configuration data as a dictionary
    test_data_directory (str): The path to the temporary test data directory

    Returns:
    None
    """
    input_path = config_data["rimworld_save_file_path"]
    output_path = tmp_path / "processed.rws"
    test_tag = "scenario"
    search_pattern = f".//{test_tag}"

    # Test the original file for one of the items that should be removed
    input_tree = xml.etree.ElementTree.parse(input_path)
    input_root = input_tree.getroot()
    input_test_element = input_root.find(search_pattern)
    assert isinstance(input_test_element, xml.etree.ElementTree.Element)
    assert input_test_element.tag == test_tag

    # Process the input file and create the processed version
    with open("defaults.json", "r", encoding="utf_8") as defaults_file:
        defaults_data = json.load(defaults_file)

    xml_elements_remove_list = defaults_data["xml_elements_remove_list"]
    xml_elements_remove_list.append(search_pattern)
    extract.modify_save_file.process_save_file(input_file_path=input_path,
        output_file_path=output_path, xml_elements_remove_list=xml_elements_remove_list)

    # Test the processed version to confirm the successful removal of items
    output_tree = xml.etree.ElementTree.parse(output_path)
    output_root = output_tree.getroot()
    output_test_element = output_root.find(search_pattern)
    assert output_test_element is None
