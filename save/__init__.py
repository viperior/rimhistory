"""Extract XML data from a RimWorld save file and return elements"""

import glob
import json
import logging
import os
import pathlib
import re
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

        # Extract singular data points
        self.data.file_size = os.path.getsize(self.data.path)
        self.data.game_version = self.data.root.find("./meta/gameVersion").text
        self.data.game_time_ticks = int(self.data.root.find(".//tickManager/ticksGame").text)

        # Extract datasets
        self.data.dataset = Bunch(
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
            }
            plant_age = element.find(".//age")

            if plant_age is None:
                current_element_data["plant_age"] = None
                logging.debug("Detected plant with no defined age:\n%s", list(element.iter()))

                for child in element:
                    logging.debug("---\n%s\n%s\n---", child.tag, child.text)
            elif isinstance(plant_age, xml.etree.ElementTree.Element):
                current_element_data["plant_age"] = plant_age.text

            current_element_data["plant_age"] = plant_age
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
        assert 1 <= len(self.data.dataset) <= 100

        logging.debug("Generating pandas DataFrames for %d datasets", len(self.data.dataset))

        for dataset_name, dataset in self.data.dataset.items():
            # Validate the input dictionary and keys
            assert isinstance(dataset, dict)
            assert isinstance(dataset_name, str)
            assert "dataframe" not in dataset.keys()

            # Generate the pandas dataframe from the list of dictionaries in dictionary_list
            dataset.dataframe = pandas.DataFrame(dataset.dictionary_list)

            # Add a time dimension for in-game time based on ticks passed
            dataset.dataframe["time_ticks"] = self.data.game_time_ticks


    def reduce_xml_data(self) -> int:
        """Remove unnecessary information from the XML tree using a list of XPath patterns

        Parameters:
        None

        Returns:
        int: The number of elements removed
        """
        total_elements_removed_count = 0

        for search_pattern in self.data.xml_elements_remove_list:
            total_elements_removed_count += self.remove_matching_elements(search_pattern)

        return total_elements_removed_count


    def remove_matching_elements(self, search_pattern: str) -> int:
        """Remove XML elements matching the given search pattern

        Parameters:
        search_pattern (str): The XPath search pattern to use to find matching elements in the tree

        Returns:
        int: The number of elements removed
        """
        elements_removed_count = 0
        sentry = True

        while sentry:
            element = self.data.root.find(search_pattern)
            starting_element_removed_count = elements_removed_count

            if element is not None:
                parent_element_search_pattern = f"{search_pattern}/.."
                parent = self.data.root.find(parent_element_search_pattern)
                assert isinstance(parent, xml.etree.ElementTree.Element)

                if parent is not None:
                    parent.remove(element)
                    elements_removed_count += 1

            # If no element was removed, stop trying to remove new occurrences
            if elements_removed_count == starting_element_removed_count:
                sentry = False

        return elements_removed_count


    def transform_plant_dataframe(self) -> None:
        """Transform the plants DataFrame by adding calculated columns

        Parameters:
        None

        Returns:
        None
        """
        # Create a column by converting plant_growth to a float and multiplying it by 100
        dataframe = self.data.dataset.plant.dataframe
        dataframe["plant_growth_percentage"] = dataframe["plant_growth"].astype(float) * 100

        # Bin the percentage values in ranges for visualization and summarized reporting
        bins = range(0, 101, 5)
        dataframe["plant_growth_bin"] = pandas.cut(dataframe["plant_growth_percentage"], bins,
            labels=bins[1:])


class SaveSeries:
    """Manage the ELT process for a series of RimWorld game save files"""
    def __init__(self, save_dir_path: pathlib.Path, save_file_regex_pattern: str) -> None:
        """Initialize the SaveSeries object

        Parameters:
        save_dir_path (pathlib.Path): The directory containing the RimWorld save files
        save_file_regex_pattern (str): A regex pattern matching a series of associated save files

        Returns:
        None
        """
        self.dictionary = {}
        logging.debug("Initializing SaveSeries object with arguments:\n\tsave_dir_path = %s\n\t\
            regex = %s", save_dir_path, save_file_regex_pattern)
        self.save_dir_path = save_dir_path
        self.save_file_regex_pattern = save_file_regex_pattern
        self.scan_save_file_dir()
        self.load_save_data()
        self.dataset = Bunch()
        self.aggregate_dataframes()


    def aggregate_dataframes(self) -> None:
        """Combine individual save datasets and group using a time dimension

        Parameters:
        None

        Returns:
        None
        """
        # Get only the keys (names of datasets) from one of the stored save datasets
        dataset_names = self.dictionary[next(iter(self.dictionary))]["save"].data.dataset.keys()
        logging.debug("Aggregating datasets: %s", dataset_names)

        for dataset_name in dataset_names:
            logging.debug("Aggregating snapshots of %s data", dataset_name)
            frame_combine_list = []

            for save_file_name, save_file_data in self.dictionary.items():
                logging.debug("Adding data from save file, %s, to %s data aggregation:\n%s",
                    save_file_name, dataset_name, save_file_data["path"])
                frame_combine_list.append(
                    save_file_data["save"].data.dataset[dataset_name].dataframe
                )

            logging.debug("Concatenating pandas dataframes into singular frame for %s data",
                dataset_name)
            self.dataset[dataset_name] = Bunch(dataframe=pandas.concat(frame_combine_list))
            logging.info("Pandas dataframe combination operation complete for %s data",
                dataset_name)


    def load_save_data(self) -> None:
        """Iterate through the save file list and store each in a Save object

        Parameters:
        None

        Returns:
        None
        """
        for save_file_base_name, save_file_dictionary in self.dictionary.items():
            logging.debug("Loading data for save file into series: %s", save_file_base_name)
            save_file_dictionary["save"] = Save(path_to_save_file=save_file_dictionary["path"])
            logging.debug("Finished loading data for save file into series: %s",
                save_file_base_name)


    def scan_save_file_dir(self) -> None:
        """Populate the dictionary property for saves files matching save_file_regex_pattern

        Parameters:
        None

        Returns:
        None
        """
        saves_all = glob.glob(f"{self.save_dir_path}/*.rws")
        logging.debug("saves_all = %s", saves_all)
        logging.debug("Using regex pattern for search = %s", self.save_file_regex_pattern)

        for save_path in saves_all:
            if re.match(self.save_file_regex_pattern, os.path.basename(save_path)):
                logging.debug("Match found in file base name: %s", os.path.basename(save_path))
            else:
                logging.debug("Match NOT found in file base name: %s", os.path.basename(save_path))

        saves_filtered = [
            save_path for save_path in saves_all\
                if re.match(self.save_file_regex_pattern, os.path.basename(save_path))
        ]
        logging.debug("saves_filtered = %s", saves_filtered)

        for save_path in saves_filtered:
            base_name = os.path.basename(save_path)
            self.dictionary[base_name] = {"path": save_path}
