"""Test the creation of a plant growth histogram from a pandas DataFrame"""

import os
import pathlib

import extract.extract_save_data
import view.summary_report


def test_plant_growth_chart(tmp_path: pathlib.Path) -> None:
    """Test the creation of a plant growth histogram from a pandas DataFrame

    Parameters:
    tmp_path (pathlib.Path): The path used to stage files needed for testing (pytest fixture)

    Returns:
    None
    """
    plant_data_raw = extract.extract_save_data.get_plant_data()
    plant_dataframe = extract.extract_save_data.plant_dataframe(dictionary_list=plant_data_raw)
    labels = {"plant_growth_bin": "Plant growth (%)"}
    plant_growth_chart_html = view.summary_report.get_histogram_html(dataframe=plant_dataframe,
        x_axis_field="plant_growth_bin", labels=labels)
    output_path = tmp_path / "plant_growth_chart.html"

    # Create the HTML file
    with open(output_path, "w", encoding="utf_8") as output_file:
        output_file.write(plant_growth_chart_html)

    # Validate the HTML file's size in bytes
    assert 3000000 <= os.path.getsize(output_path) <= 10000000

    # Validate the HTML content contains the expected boilerplate text from plotly
    with open(output_path, "r", encoding="utf_8") as chart_file:
        assert "plotly.js v" in chart_file.read()
