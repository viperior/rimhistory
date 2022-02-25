"""Test the Save class"""

import gzip
import logging
import pathlib
import shutil
import xml.etree.ElementTree

from save import Save


def test_class_save_pawn(test_data_list: list) -> None:
    """Test the Save class's pawn property

    Parameters:
    test_data_list (list): The list of paths to the test input data files (fixture)

    Returns:
    None
    """
    save = Save(path_to_save_file=test_data_list[0])
    pawn_data = save.data.dataset.pawn.dictionary_list

    # Test the pawn property's data type
    assert isinstance(pawn_data, list)

    # Test the number of pawns detected
    assert 1 <= len(pawn_data) <= 150
    logging.debug("Found pawn = %s", pawn_data[0]["pawn_id"])

    # Test the length of the first pawn_id
    assert 3 <= len(pawn_data[0]["pawn_id"]) <= 50


def test_class_save_root(test_data_list: list) -> None:
    """Test the Save class's root property

    Parameters:
    test_data_list (list): The list of paths to the test input data files (fixture)

    Returns:
    None
    """
    root = Save(test_data_list[0], preserve_root=True).data.root

    # Test the Save class's root property data type
    assert isinstance(root, xml.etree.ElementTree.Element)

    # Validate that the XML tree contains the pawnData element
    element = root.find(".//pawnData")

    # Validate the sample element's data type
    assert isinstance(element, xml.etree.ElementTree.Element)
    logging.debug("pawnData element = %s", element.tag)

    for index, child in enumerate(element):
        logging.debug("child element #%d data = %s, %s", index, child.tag, child.text)


def test_game_time_ticks(test_data_list: list) -> None:
    """Test the Save class's game_time_ticks property

    Parameters:
    test_data_list (list): The list of paths to the test input data files (fixture)

    Returns:
    None
    """
    game_time_ticks = Save(test_data_list[0]).data.game_time_ticks
    logging.debug("game_time_ticks = %d", game_time_ticks)
    assert isinstance(game_time_ticks, int)
    assert game_time_ticks == 41164371


def test_null_handling(test_data_list: list) -> None:
    """Test the Save class's add_value_to_dictionary_from_xml_with_null_handling function

    Parameters:
    test_data_list (list): The list of paths to the test input data files (fixture)

    Returns:
    None
    """
    child_element_tag = "test_child"
    parent_element_tag = "test_parent"
    parent_element = xml.etree.ElementTree.Element(parent_element_tag)
    child_element = xml.etree.ElementTree.SubElement(parent_element, child_element_tag)
    xml.etree.ElementTree.SubElement(parent_element, "another_child")
    child_element_text = "99.99999"
    child_element.text = child_element_text
    target_key = "test_key"

    # Test adding a plant's growth value when it should be present
    assert isinstance(child_element, xml.etree.ElementTree.Element)
    assert child_element.tag == child_element_tag
    test_dictionary = {}
    assert isinstance(test_dictionary, dict)
    assert target_key not in test_dictionary
    save = Save(path_to_save_file=test_data_list[0])
    save.add_value_to_dictionary_from_xml_with_null_handling(
        dictionary=test_dictionary,
        xml_element=child_element,
        parent_element=parent_element,
        column_name=target_key
    )
    assert target_key in test_dictionary
    assert isinstance(test_dictionary[target_key], str)
    assert len(test_dictionary[target_key]) > 2
    assert test_dictionary[target_key] == child_element_text

    # Test again when the target element is missing
    test_dictionary = {}
    parent_element.remove(child_element)
    child_element = parent_element.find(f".//{child_element_tag}")
    assert isinstance(test_dictionary, dict)
    assert target_key not in test_dictionary
    save.add_value_to_dictionary_from_xml_with_null_handling(
        dictionary=test_dictionary,
        xml_element=child_element,
        parent_element=parent_element,
        column_name=target_key
    )
    assert target_key in test_dictionary
    assert test_dictionary[target_key] is None


def test_uncompressed_file(test_data_list: list, tmp_path: pathlib.Path) -> None:
    """Test the Save class using an uncompressed source file

    Parameters:
    test_data_list (list): The list of paths to the test input data files (fixture)
    tmp_path (pathlib.Path): The path used to stage files needed for testing (fixture)

    Returns:
    None
    """
    # Create an uncompressed save file to use for testing
    compressed_save_file_path = test_data_list[0]
    uncompressed_save_file_path = tmp_path / "uncompressed save 1.rws"

    with gzip.open(compressed_save_file_path, "rb") as compressed_file:
        with open(uncompressed_save_file_path, "wb") as uncompressed_file:
            shutil.copyfileobj(compressed_file, uncompressed_file)

    # Create a Save object from the uncompressed file
    save = Save(path_to_save_file=uncompressed_save_file_path)

    # Perform basic checks on the created Save object
    assert isinstance(save, Save)
    assert "plant" in save.data.dataset.keys()
    assert 1 <= len(save.data.dataset.pawn) <= 50
