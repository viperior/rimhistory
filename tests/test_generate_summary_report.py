"""Test the view.summary_report.generate_summary_report function"""

import logging

import pytest

import view.summary_report


def get_test_input_data() -> list:
    """Return a list of dictionaries containing test input metadata

    Parameters:
    None

    Returns:
    list: A list of dictionaries with test input metadata
    """
    test_input = [
        {
            "output_file_name_base": "summary_report_test_001"
        },
        {
            "output_file_name_base": "summary_report_test_002"
        }
    ]

    return test_input


@pytest.mark.parametrize("test_input", get_test_input_data())
def test_generate_summary_report(test_input: list, test_data_directory: str) -> None:
    """Test the view.summary_report.generate_summary_report function

    Parameters:
    test_input (list): The list of test input items
    test_data_directory (str): The path to the temporary test data directory

    Returns:
    None
    """
    output_directory = f"{test_data_directory}/reports"

    # Generate the report
    view.summary_report.generate_summary_report(output_directory=output_directory,
        output_file_name=test_input["output_file_name_base"])
    output_path = f"{output_directory}/{test_input['output_file_name_base']}.html"

    # Test the generated report
    with open(output_path, "r", encoding="utf_8") as report_file:
        doctype = report_file.readline()

        # Check for a DOCTYPE tag on the first line
        assert "DOCTYPE" in doctype
        minimum_line_count_sentry = False

        for line_counter, line in enumerate(report_file):
            # Log the XML line data every 10th line at the DEBUG level
            if line_counter % 10 == 0:
                logging.debug(line)

            # The report XML should have at least 20 lines of content
            if line_counter >= 20:
                minimum_line_count_sentry = True

    # Check whether the generated file exceeds a minimum line length threshold
    assert minimum_line_count_sentry is True
