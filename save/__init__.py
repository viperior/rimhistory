"""Extract XML data from a RimWorld save file and return elements"""

import gzip
import logging
import multiprocessing
import os
import pathlib
import re
import xml.etree.ElementTree

from bunch import Bunch
import pandas
import wcmatch.pathlib


class Save:
    """Extract the XML data from a RimWorld save file and return the elements"""
    def __init__(self, path_to_save_file: pathlib.Path, preserve_root: bool = False) -> None:
        """Initialize the Save object by parsing the root XML object using ElementTree

        Parameters:
        path_to_save_file (pathlib.Path): The path to the RimWorld save file to be loaded
        preserve_root (bool): Keeps the XML root element available for access if True

        Returns:
        None
        """
        self.data = Bunch()
        self.data.path = path_to_save_file
        self.data.file_base_name = os.path.basename(self.data.path)

        # Parse the XML document and get the root
        if os.path.splitext(self.data.path)[1] == ".gz":
            # Handle gzip compressed files
            with gzip.open(self.data.path, "rb") as save_file:
                self.data.root = xml.etree.ElementTree.parse(save_file).getroot()
        else:
            self.data.root = xml.etree.ElementTree.parse(self.data.path).getroot()

        # Extract singular data points
        self.data.file_size = os.path.getsize(self.data.path)
        self.data.game_version = self.data.root.find("./meta/gameVersion").text
        self.data.game_time_ticks = int(self.data.root.find(".//tickManager/ticksGame").text)

        # Extract datasets
        self.data.dataset = Bunch(
            mod=Bunch(dictionary_list=self.extract_mod_list()),
            pawn=Bunch(dictionary_list=self.extract_pawn_data()),
            plant=Bunch(dictionary_list=self.extract_plant_data()),
            weather=Bunch(dictionary_list=self.extract_weather_data()),
        )

        # Delete the root object to free up memory
        if not preserve_root:
            del self.data.root

        # Generate pandas DataFrames from each dataset initialized as a list of dictionaries
        self.generate_dataframes()

        # Apply transformations to DataFrames
        self.transform_pawn_dataframe()
        self.transform_plant_dataframe()

        logging.info("Finished creating new Save object from file: %s", self.data.path)

    @staticmethod
    def add_value_to_dictionary_from_xml_with_null_handling(
            dictionary: dict, xml_element: xml.etree.ElementTree.Element,
            parent_element: xml.etree.ElementTree.Element, column_name: str) -> None:
        """Add a value to to key, column name, to the given dictionary source from xml_element

        Parameters:
        dictionary (dict): The dictionary to add the value to
        xml_element (xml.etree.ElementTree.Element): The source XML element for the current row
        parent_element (xml.etree.ElementTree.Element): The parent element of the source element
        column_name (str): The name of the key/column to add to the dictionary

        Returns:
        None
        """
        if xml_element is None:
            dictionary[column_name] = None
            xml_content_dump = ""

            for child in parent_element:
                xml_content_dump += (
                    f"<{child.tag} {{attribs = {child.attrib}}}>{child.text}</{child.tag}>\n"
                )

            logging.debug("XML content with undefined %s\n%s", column_name, xml_content_dump)
        elif isinstance(xml_element, xml.etree.ElementTree.Element):
            dictionary[column_name] = xml_element.text

    def add_values_to_dictionary(self, dictionary: dict, xpath_pattern_key_list: list,
                                 parent_element: xml.etree.ElementTree.Element) -> None:
        """Add values to the given dictionary given the input list of xpath_patterns and target keys

        Parameters:
        dictionary (dict): The dictionary to add the entries to
        xpath_pattern_key_list (list): A list of tuples of XPath patterns and associated key names
        parent_element (xml.etree.ElementTree.Element): The parent XML element containing the data

        Returns:
        None
        """
        for target_key, xpath_pattern in xpath_pattern_key_list:
            self.add_value_to_dictionary_from_xml_with_null_handling(
                dictionary=dictionary,
                xml_element=parent_element.find(xpath_pattern),
                parent_element=parent_element,
                column_name=target_key
            )

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
                "tale_date": element.find(".//date").text,
            }
            xpath_pattern_key_list = [
                ("pawn_name_nick", ".//pawnData/name/nick"),
                ("pawn_name_last", ".//pawnData/name/last"),
                ("pawn_biological_age", ".//pawnData/age"),
                ("pawn_chronological_age", ".//pawnData/chronologicalAge"),
                ("pawn_ambient_temperature", ".//surroundings/temperature"),
                ("pawn_name_first", ".//pawnData/name/first"),
            ]
            self.add_values_to_dictionary(
                dictionary=current_pawn,
                xpath_pattern_key_list=xpath_pattern_key_list,
                parent_element=element
            )
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
            }
            xpath_pattern_key_list = [
                ("plant_definition", ".//def"),
                ("plant_map_id", ".//map"),
                ("plant_position", ".//pos"),
                ("plant_growth", ".//growth"),
                ("plant_age", ".//age"),
            ]
            self.add_values_to_dictionary(
                dictionary=current_element_data,
                xpath_pattern_key_list=xpath_pattern_key_list,
                parent_element=element
            )
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

    def transform_pawn_dataframe(self) -> None:
        """Apply transformations to the pawn DataFrame

        Parameters:
        None

        Returns:
        None
        """
        # Convert the tale_date column from a string to an integer
        dataframe = self.data.dataset.pawn.dataframe
        dataframe["tale_date_integer"] = dataframe["tale_date"].astype(int)
        dataframe.drop(columns=["tale_date"])
        dataframe.rename(columns={"tale_date_integer": "tale_date"})

        # Determine the current record (latest chronological) for each unique pawn
        dataframe["tale_date_max"] = dataframe.groupby(["pawn_id"])["tale_date"].transform(max)
        dataframe["current_record"] = dataframe["tale_date_max"] == dataframe["tale_date"]
        dataframe["is_humanoid_colonist"] = dataframe["pawn_id"].str.contains("Thing_Android")

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
        dataframe["plant_growth_bin"] = pandas.cut(dataframe["plant_growth_percentage"],
                                                   bins, labels=bins[1:])


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
        # Validate that there are dataframes present to aggregate before continuing
        if len(self.dictionary) < 1:
            logging.error("0 source dataframes detected while attempting to aggregate frames")
            assert len(self.dictionary) > 0

        # Get only the keys (names of datasets) from one of the stored save datasets
        dataset_names = self.dictionary[list(self.dictionary.keys())[0]]["save"].data.dataset.keys()
        logging.debug("Aggregating datasets: %s", dataset_names)

        for dataset_name in dataset_names:
            logging.debug("Aggregating snapshots of %s data", dataset_name)
            frame_combine_list = []

            for save_file_name, save_file_data in self.dictionary.items():
                logging.debug("Adding data from save file, %s, to %s data aggregation:\n%s",
                              save_file_name, dataset_name, save_file_data["path"])
                current_dataframe = save_file_data["save"].data.dataset[dataset_name].dataframe
                frame_combine_list.append(current_dataframe)

            logging.debug("Concatenating pandas dataframes into singular frame for %s data",
                          dataset_name)
            self.dataset[dataset_name] = Bunch(dataframe=pandas.concat(frame_combine_list))
            logging.info("Pandas dataframe combination operation complete for %s data",
                         dataset_name)

    @property
    def latest_save(self) -> Save:
        """Return the chronologically latest save by reading the in-game time of each save

        Parameters:
        None

        Returns:
        Save: The Save object containing the latest sava data
        """
        max_time_value = 0
        latest_save = None
        latest_save_name = None

        for save_name, save in self.dictionary.items():
            current_time_value = save["save"].data.game_time_ticks
            logging.debug("Checking in-game time for save: %s", save_name)
            logging.debug("save.data.game_time_ticks > max_time_ticks_value == %s",
                          current_time_value > max_time_value)

            if current_time_value > max_time_value:
                logging.debug("New max time ticks value identified = %d", current_time_value)
                max_time_value = current_time_value
                latest_save = save
                latest_save_name = save_name

        logging.info("Identified save, %s, as the latest save, with %d ticks", latest_save_name,
                     max_time_value)

        return latest_save

    def load_save_data(self) -> None:
        """Iterate through the save file list and store each in a Save object

        Parameters:
        None

        Returns:
        None
        """
        logging.debug("Creating worker pool")

        with multiprocessing.Pool() as pool:
            result = pool.map(self.load_save_data_worker_task, list(self.dictionary.keys()))

        logging.info("All work given to the worker pool has been completed (%d tasks)",
                     len(result))
        logging.debug("result = %s", result)
        logging.debug("Joining results from worker pool tasks")

        for save in result:
            self.dictionary[save.data.file_base_name]["save"] = save

        logging.debug("Successfully loaded save data using worker pool")

    def load_save_data_worker_task(self, save_base_name: str) -> Save:
        """Execute the load operation for a single save file

        Parameters:
        save_base_name (str): The base name of the save, which is used as the reference key

        Returns:
        Save: The loaded Save object
        """
        logging.debug("Worker starting to process save: %s", save_base_name)
        save_path = self.dictionary[save_base_name]["path"]
        current_save = Save(path_to_save_file=save_path)
        logging.debug("Worker is finished processing save: %s", save_base_name)
        logging.debug("Showing current view of self.dictionary.keys() = \n%s",
                      self.dictionary.keys())

        for key, value in self.dictionary.items():
            logging.debug("Keys for save, %s: %s", key, value.keys())

        return current_save

    def scan_save_file_dir(self) -> None:
        """Populate the dictionary property for saves files matching save_file_regex_pattern

        Parameters:
        None

        Returns:
        None
        """
        saves_all = list(wcmatch.pathlib.Path(self.save_dir_path).glob(["*.rws", "*.rws.gz"]))
        logging.debug("saves_all = %s", saves_all)
        logging.debug("Using regex pattern for search = %s", self.save_file_regex_pattern)

        for save_path in saves_all:
            if re.match(self.save_file_regex_pattern, os.path.basename(save_path)):
                logging.debug("Match found in file base name: %s", os.path.basename(save_path))
            else:
                logging.debug("Match NOT found in file base name: %s", os.path.basename(save_path))

        pattern = self.save_file_regex_pattern
        saves_filtered = [
            save_path for save_path in saves_all if re.match(pattern, os.path.basename(save_path))
        ]
        logging.debug("saves_filtered = %s", saves_filtered)

        if len(saves_filtered) < 1:
            logging.error("0 saves were processed\nAll saves = %s\nFiltered saves = %s", saves_all,
                          saves_filtered)

        for save_path in saves_filtered:
            base_name = os.path.basename(save_path)
            self.dictionary[base_name] = {"path": save_path}
