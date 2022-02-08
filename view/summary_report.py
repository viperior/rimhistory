"""Generate a summary HTML report for RimWorld save game data"""

import pathlib

import dominate
from dominate.tags import attr, div, h1, h2, li, link, p, ul

import extract.extract_save_data


def generate_summary_report(output_path: pathlib.Path) -> None:
    """Generate an HTML report with a list of the installed mods found

    Parameters:
    output_path (pathlib.Path): The file path where the report should be created

    Returns:
    None
    """
    mod_list = extract.extract_save_data.extract_mod_list()
    doc = dominate.document(title='RimWorld Save Game Summary Report')

    with doc.head:
        link(rel='stylesheet', href='style.css')

    with doc:
        with div():
            attr(cls='body')
            h1("RimWorld Save Game Summary")
            h2("Game Version")
            p(extract.extract_save_data.extract_game_version())
            h2("File Size")
            p(f"{extract.extract_save_data.get_save_file_size()} bytes")
            h2(f"Installed Mods ({len(mod_list)})")

            with ul():
                for mod in mod_list:
                    mod_list_item_content = mod["mod_name"]
                    mod_steam_id = mod["mod_steam_id"]

                    if mod_steam_id and mod_steam_id != "0":
                        mod_list_item_content += f" (Steam ID: {mod['mod_steam_id']})"

                    li(mod_list_item_content)

            h2(f"Colonists ({extract.extract_save_data.get_pawn_count()})")

            with ul():
                for pawn in extract.extract_save_data.get_pawn_data():
                    li(f"{pawn['pawn_name_full']}, age {pawn['pawn_biological_age']}")

            h2(f"Plants ({extract.extract_save_data.get_plant_count()})")
            plant_data_raw = extract.extract_save_data.get_plant_data()

            with ul():
                displayed_plant_types = []

                for plant in plant_data_raw:
                    if plant['plant_definition'] in displayed_plant_types:
                        continue

                    displayed_plant_types.append(plant['plant_definition'])
                    plant_information = (
                        f"{plant['plant_definition']} - "
                        f"{plant['plant_growth']} - "
                        f"{plant['plant_position']}"
                    )
                    li(plant_information)

                    if len(displayed_plant_types) >= 20:
                        break

            plant_dataframe = extract.extract_save_data.plant_dataframe(dictionary_list=\
                plant_data_raw)
            p(dominate.util.raw(plant_dataframe.head().to_html()))
            p(dominate.util.raw(plant_dataframe.tail().to_html()))
            p(dominate.util.raw(plant_dataframe.describe().to_html()))
            p(dominate.util.raw(plant_dataframe["plant_definition"].value_counts().to_frame().to_html()))

    with open(output_path, "w", encoding="utf_8") as output_file:
        output_file.write(str(doc))
