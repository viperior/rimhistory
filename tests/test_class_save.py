"""Test the Save class"""

import logging
import xml.etree.ElementTree

import extract.save


def test_class_save_pawn(config_data: dict) -> None:
    """Test the Save class's pawn property

    Parameters:
    config_data (dict): The project configuration data as a dictionary (fixture)

    Returns:
    None
    """
    save = extract.save.Save(config_data["rimworld_save_file_path"])
    pawn_data = save.pawn

    # Test the pawn property's data type
    assert isinstance(pawn_data, list)

    # Test the number of pawns detected
    assert 1 <= len(pawn_data) <= 150
    logging.debug("Found pawn = %s", pawn_data[0]["pawn_id"])

    # Test the length of the first pawn_id
    assert 3 <= len(pawn_data[0]["pawn_id"]) <= 50


def test_class_save_root(config_data: dict) -> None:
    """Test the Save class's root property

    Parameters:
    config_data (dict): The project configuration data as a dictionary (fixture)

    Returns:
    None
    """
    save = extract.save.Save(config_data["rimworld_save_file_path"]).root

    # Test the Save class's root property data type
    assert isinstance(save, xml.etree.ElementTree.Element)

    # Validate that the XML tree contains the pawnData element
    element = save.find(".//pawnData")

    # Validate the sample element's data type
    assert isinstance(element, xml.etree.ElementTree.Element)
    logging.debug("pawnData element = %s", element.tag)

    for index, child in enumerate(element):
        logging.debug("child element #%d data = %s, %s", index, child.tag, child.text)
