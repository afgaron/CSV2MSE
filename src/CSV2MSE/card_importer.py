import configparser
import csv
import os
import shutil
from tkinter import filedialog as fd
from typing import Iterable

import card_parser


def read_config_file(file: str) -> tuple[dict[str, str], dict[str, str]]:
    """
    Read the configuration details given in the provided config file. Returns two
    dictionaries: one with metadata about the set, and one with mappings between
    the CSV file and the canonical MSE field names.
    """
    if not os.path.exists(file):
        raise FileNotFoundError("Can't find metadata.cfg in working directory")

    config = configparser.ConfigParser()
    config.read(file, encoding="utf8")

    metadata = {
        key: config["set_info"].get(key)
        for key in config["set_info"]
        if config["set_info"].get(key)
    }

    metadata["title"] = metadata.get("title", "untitled")

    columns = {key: config["card"].get(key).lower() or key for key in config["card"]}

    return metadata, columns


def create_set_dir(metadata: dict[str, str]) -> str:
    """
    Generate an empty set file for MSE 2.0 and add any set details from the metadata
    dictionary. Defaults to using the m15-altered stylesheet. Returns name of set file.
    """
    set_dir = metadata["title"] + ".mse-set"

    # Check to overwrite existing folder
    if os.path.exists(set_dir):
        overwrite = ""
        while overwrite.lower() not in ["y", "n"]:
            overwrite = input("Overwrite existing folder? Y/N: ")
        if overwrite.lower() == "y":
            try:
                os.remove(set_dir)
            except:
                shutil.rmtree(set_dir)
        else:
            print("Aborting.")
            return

    os.mkdir(set_dir)

    with open(set_dir + "/set", "w", encoding="utf8") as f:
        f.write("mse_version: 2.0.0\n")
        f.write("game: magic\n")
        f.write("stylesheet: m15-altered\n")
        f.write("set_info:\n")
        for key in metadata:
            f.write(f"\t{key}: {metadata[key]}\n")

    return set_dir


def read_csv() -> list[dict[str, str]]:
    """
    Prompt the user to select a CSV file, then import each line as a dictionary
    mapping the row's value to the column name. Returns list of cards.
    """
    filename = fd.askopenfilename()

    header, body = [], []
    with open(filename, "r", encoding="utf8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not header:
                header = row
            # On subsequent loops, read card info but skip blank lines
            elif any(len(r) for r in row):
                body.append(
                    {key.strip().lower(): val.strip() for key, val in zip(header, row)}
                )

    return body


def process_csv(
    set_dir: str, column_mapping: dict[str, str], cards: Iterable[dict[str, str]]
) -> None:
    """
    Given a list of cards and a mapping dictionary to translate to MSE attributes,
    write each card to a file in the set directory.
    """
    with open(set_dir + "/set", "a", encoding="utf8") as set_file:
        for ix, card in enumerate(cards):
            # Check for duplicate card names
            filename = (
                card_parser.fix_file_name(card.get(column_mapping["name"]))
                or f"untitled {ix}"
            )
            if os.path.exists(f"{set_dir}/card {filename}"):
                filename += f" {ix}"

            # Write each card to its own file
            with open(f"{set_dir}/card {filename}", "w", encoding="utf8") as card_file:
                card_file.write("mse_version: 2.0.0\n")
                card_file.write("card:\n")

                # If card_type is provided, combine it with super_type
                card_parser.fix_card_type(card, column_mapping)

                # Set stylesheet for certain card types
                card_parser.fix_stylesheet(card, column_mapping)

                # Planeswalkers have their own rules box
                card_parser.fix_planeswalker_rule_text(card, column_mapping)

                for col in column_mapping:
                    # Some columns with need additional formatting fixes
                    if "card_type" in col:
                        continue
                    elif "rarity" in col:
                        val = card_parser.fix_rarity(card.get(column_mapping[col]))
                    elif "text" in col and card.get(column_mapping[col]):
                        val = card_parser.fix_multiline_text(
                            card.get(column_mapping[col])
                        )
                        val = card_parser.fix_symbols(val)
                        card_name = card.get(
                            column_mapping[f"name{'_2' if '2' in col else ''}"]
                        )
                        val = card_parser.fix_name_in_text(val, card_name)
                    elif "name" in col:
                        val = card_parser.fix_symbols(card.get(column_mapping[col]))
                        val = val.replace("\n", " ")
                    elif "stylesheet" in col and not card.get(column_mapping[col]):
                        continue
                    elif (
                        "power" in col or "toughness" in col or "loyalty" in col
                    ) and not card_parser.needs_power_toughness_loyalty(
                        col, card, column_mapping
                    ):
                        continue
                    else:
                        val = card.get(column_mapping[col], "")
                    card_file.write(f"\t{col}: {val}\n")

                # Add time the card was written
                now = card_parser.get_current_timestamp()
                card_file.write(f"\ttime_created: {now}\n")
                card_file.write(f"\ttime_modified: {now}\n")

            # Update the set file to include the card
            # MSE should combine it all into one file automatically
            set_file.write(f"include_file: card {filename}\n")


def zip_set_dir(set_dir: str) -> None:
    """
    Take the directory containing the set file and zip it so that MSE can open it.
    """
    set_name = set_dir.split(".mse-set")[0]
    shutil.make_archive(set_name, "zip", set_dir)
    shutil.rmtree(set_dir)
    os.rename(set_name + ".zip", set_dir)
