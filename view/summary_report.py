"""Generate a summary HTML report for RimWorld save game data"""

import dominate
from dominate.tags import attr, div, h1, h2, li, link, p, ul

import extract.extract_save_data


def generate_summary_report() -> None:
    """Generate an HTML report with a list of the installed mods found

    Parameters:
    None

    Returns:
    None
    """
    mod_list = extract.extract_save_data.extract_mod_list()
    output_path = "data/reports/summary.html"
    doc = dominate.document(title='RimWorld Save Game Summary Report')

    with doc.head:
        link(rel='stylesheet', href='style.css')

    with doc:
        with div():
            attr(cls='body')
            h1("RimWorld Save Game Summary")
            h2("File Size")
            p(f"{extract.extract_save_data.get_save_file_size()} bytes")
            h2(f"Installed Mods ({len(mod_list)})")

            with ul():
                for mod in mod_list:
                    li(mod["mod_name"])

    with open(output_path, "w", encoding="utf_8") as output_file:
        output_file.write(str(doc))


if __name__ == "__main__":
    generate_summary_report()
