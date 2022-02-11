"""Extract XML data from a RimWorld save file and return elements"""

import json
import logging
import os
import pathlib
import xml.etree.ElementTree

from bunch import Bunch
import pandas


class Save:
    """Extract the XML data from a RimWorld save file and return the elements"""
    def __init__(self, path_to_save_file: pathlib.Path) -> None:
        """Initialize the Save object by parsing the root XML object using ElementTree

        Parameters:
        path_to_save_file (pathlib.Path): The path to the RimWorld save file to be loaded

        Returns:
        None
        """
        self.data = Bunch()
        self.data.path = path_to_save_file

        # Parse the XML document and get the root
        self.data.root = xml.etree.ElementTree.parse(self.data.path).getroot()

        # Pre-process the save file by removing extraneous information
        with open("defaults.json", "r", encoding="utf_8") as defaults_file:
            defaults_data = json.load(defaults_file)

        self.data.xml_elements_remove_list = defaults_data["xml_elements_remove_list"]
        self.reduce_xml_data()

        # Extract singular data points
        self.data.file_size = os.path.getsize(self.data.path)
        self.data.game_version = self.data.root.find("./meta/gameVersion").text

        # Extract datasets
        self.data.datasets = Bunch(
            mod = Bunch(dictionary_list = self.extract_mod_list()),
            pawn = Bunch(dictionary_list = self.extract_pawn_data()),
            plant = Bunch(dictionary_list = self.extract_plant_data()),
            weather = Bunch(dictionary_list = self.extract_weather_data()),
        )

        # Generate pandas DataFrames from each dataset initialized as a list of dictionaries
        self.generate_dataframes()

        # Apply transformations to DataFrames
        self.transform_plant_dataframe()


    def extract_mod_list(self) -> list:
        """Extract the list of mods installed in the save game

        Parameters:
        None

        Returns:
        list: A list of dictionaries with each installed mod's metadata
        """
        mod_ids = self.data.root.findall("./meta/modIds")
        mod_steam_ids = self.data.root.findall("./meta/modSteamIds")
        mod_names = self.data.root.findall("./meta/modNames")
        mod_list = []

        for index, mod_id in enumerate(mod_ids[0]):
            mod_info = {
                "mod_id": mod_id.text,
                "mod_name": mod_names[0][index].text,
                "mod_steam_id": mod_steam_ids[0][index].text
            }
            mod_list.append(mod_info)

        return mod_list


    def extract_pawn_data(self) -> list:
        """Return a list of dictionaries containing pawn data

        Parameters:
        None

        Returns:
        list: The list of dictionaries containing pawn data
        """
        pawn_data_elements = self.data.root.findall(".//li[@Class='Tale_SinglePawn']")
        pawn_data = []

        for element in pawn_data_elements:
            current_pawn = {
                "pawn_id": element.find(".//pawnData/pawn").text,
                "pawn_name_first": element.find(".//pawnData/name/first").text,
                "pawn_name_nick": element.find(".//pawnData/name/nick").text,
                "pawn_name_last": element.find(".//pawnData/name/last").text,
                "pawn_biological_age": element.find(".//pawnData/age").text,
                "pawn_chronological_age": element.find(".//pawnData/chronologicalAge").text,
                "pawn_ambient_temperature": element.find(".//surroundings/temperature").text,
            }
            current_pawn["pawn_name_full"] = (
                f"{current_pawn['pawn_name_first']} "
                f"\"{current_pawn['pawn_name_nick']}\" "
                f"{current_pawn['pawn_name_last']}"
            )
            pawn_data.append(current_pawn)

        return pawn_data


    def extract_plant_data(self) -> list:
        """Return a list of dictionaries containing plant data

        Parameters:
        None

        Returns:
        list: The list of dictionaries containing plant data
        """
        search_pattern = ".//thing[@Class='Plant']"
        xml_elements = self.data.root.findall(search_pattern)
        plant_data = []

        for element in xml_elements:
            current_element_data = {
                "plant_id": element.find(".//id").text,
                "plant_definition": element.find(".//def").text,
                "plant_map_id": element.find(".//map").text,
                "plant_position": element.find(".//pos").text,
                "plant_growth": element.find(".//growth").text,
                "plant_age": element.find(".//age").text,
            }
            plant_data.append(current_element_data)

        return plant_data


    def extract_weather_data(self) -> dict:
        """Return the weather data for the current map

        Parameters:
        None

        Returns:
        dict: A dictionary containing weather data for the current map
        """
        element = self.data.root.find(".//weatherManager")
        weather_data = {
            "weather_current": element.find(".//curWeather").text,
            "weather_current_age": element.find(".//curWeatherAge").text,
            "weather_last": element.find(".//lastWeather").text,
        }

        # Nest the weather dictionary inside a list to maintain list of dictionaries as the return
        weather_data_list = [weather_data]

        return weather_data_list


    def generate_dataframes(self) -> None:
        """Generate pandas DataFrames for each dataset

        Parameters:
        None

        Returns:
        None
        """
        # Validate the input list length
        assert 1 <= len(self.data.datasets) <= 100

        logging.debug("Generating pandas DataFrames for %d datasets", len(self.data.datasets))

        for dataset_name, dataset in self.data.datasets.items():
            # Validate the input dictionary and keys
            assert isinstance(dataset, dict)
            assert isinstance(dataset_name, str)
            assert "dataframe" not in dataset.keys()

            # Generate the pandas dataframe from the list of dictionaries in dictionary_list
            dataset.dataframe = pandas.DataFrame(dataset.dictionary_list)


    def reduce_xml_data(self) -> None:
        """Remove unnecessary information from the XML tree using a list of XPath patterns

        Parameters:
        None

        Returns:
        None
        """

        for search_pattern in self.data.xml_elements_remove_list:
            logging.debug("Removing XML elements matching search pattern: %s", search_pattern)
            self.remove_matching_elements(search_pattern=search_pattern)


    def remove_matching_elements(self, search_pattern: str) -> None:
        """Remove XML elements matching the given search pattern

        Parameters:
        search_pattern (str): The XPath search pattern to use to find matching elements in the tree

        Returns:
        None
        """
        elements_removed_count = 0
        sentry = True

        while sentry:
            element = self.data.root.find(search_pattern)
            starting_element_removed_count = elements_removed_count

            if element is None:
                logging.debug("Element matching pattern (%s) not found", search_pattern)
            else:
                logging.debug("Element matching pattern found: %s; Targeting parent element",
                    element.tag)
                parent_element_search_pattern = f"{search_pattern}/.."
                parent = self.data.root.find(parent_element_search_pattern)
                assert isinstance(parent, xml.etree.ElementTree.Element)

                if parent is not None:
                    logging.debug("Parent element found. Proceeding with removal of child element")
                    parent.remove(element)
                    elements_removed_count += 1

            # If no element was removed, stop trying to remove new occurrences
            if elements_removed_count == starting_element_removed_count:
                sentry = False

        logging.debug("%d elements removed total", elements_removed_count)


    def transform_plant_dataframe(self) -> None:
        """Transform the plants DataFrame by adding calculated columns

        Parameters:
        None

        Returns:
        None
        """
        # Create a column by converting plant_growth to a float and multiplying it by 100
        dataframe = self.data.datasets.plant.dataframe
        dataframe["plant_growth_percentage"] = dataframe["plant_growth"].astype(float) * 100

        # Bin the percentage values in ranges for visualization and summarized reporting
        bins = range(0, 101, 5)
        dataframe["plant_growth_bin"] = pandas.cut(dataframe["plant_growth_percentage"], bins,
            labels=bins[1:])
