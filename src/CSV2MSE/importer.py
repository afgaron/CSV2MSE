import configparser
import csv
import os
import shutil
from tkinter import filedialog as fd
from typing import Iterable

import parser


def read_config_file(file: str) -> tuple[dict[str, str], dict[str, str]]:
    """
    Read the configuration details given in the provided config file. Returns two
    dictionaries: one with metadata about the set, and one with mappings between
    the CSV file and the canonical MSE field names.
    """
    if not os.path.exists(file):
        raise FileNotFoundError("Can't find metadata.cfg in working directory")

    config = configparser.ConfigParser()
    config.read(file)

    metadata = {
        key: config["set_info"].get(key)
        for key in config["set_info"]
        if config["set_info"].get(key)
    }

    columns = {
        key: config["card"].get(key).lower()
        for key in config["card"]
        if config["card"].get(key)
    }

    # These columns must exist for planeswalkers to work
    columns["stylesheet"] = columns.get("stylesheet", "stylesheet")
    columns["level_1_text"] = columns.get("level_1_text", "level_1_text")

    return metadata, columns


def create_set_dir(metadata: dict[str, str]) -> str:
    """
    Generate an empty set file for MSE 2.0 and add any set details from the metadata
    dictionary. Defaults to using the m15-altered stylesheet. Returns name of set file.
    """
    if not metadata.get("title"):
        metadata["title"] = "Untitled"

    set_dir = metadata["title"] + ".mse-set"
    os.mkdir(set_dir)

    with open(set_dir + "/set", "w") as f:
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
    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            # On first loop, read the header
            if not header:
                header = row
            # On subsequent loops, read card info
            else:
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
    with open(set_dir + "/set", "a") as set_file:
        for ix, card in enumerate(cards):
            name = card.get(column_mapping["name"]) or f"untitled {ix}"

            # Write each card to its own file
            with open(f"{set_dir}/card {name}", "w") as card_file:
                card_file.write("mse_version: 2.0.0\n")
                card_file.write("card:\n")

                # If card_type is provided, combine it with super_type
                parser.fix_card_type(card, column_mapping)

                # Set stylesheet for planeswalkers and battles
                parser.fix_stylesheet(card, column_mapping)

                # Planeswalkers have their own rules box
                parser.fix_planeswalker_rule_text(card, column_mapping)

                for col in column_mapping:
                    # Some columns with need additional formatting fixes
                    if "card_type" in col:
                        continue
                    elif "rarity" in col:
                        val = parser.fix_rarity(card.get(column_mapping[col]))
                    elif "text" in col and card.get(column_mapping[col]):
                        val = parser.fix_multiline_text(card.get(column_mapping[col]))
                        val = parser.fix_symbols(val)
                    elif "name" in col:
                        val = parser.fix_symbols(card.get(column_mapping[col]))
                    elif "stylesheet" in col and not card.get(column_mapping[col]):
                        continue
                    else:
                        val = card.get(column_mapping[col], "")
                    card_file.write(f"\t{col}: {val}\n")

                # Add time the card was written
                now = parser.get_current_timestamp()
                card_file.write(f"\ttime_created: {now}\n")
                card_file.write(f"\ttime_modified: {now}\n")

            # Update the set file to include the card
            # MSE should combine it all into one file automatically
            set_file.write(f"include_file: card {name}\n")


def zip_set_dir(set_dir: str) -> None:
    """
    Take the directory containing the set file and zip it so that MSE can open it.
    """
    set_name = set_dir.split(".mse-set")[0]
    shutil.make_archive(set_name, "zip", set_dir)
    shutil.rmtree(set_dir)
    os.rename(set_name + ".zip", set_dir)
