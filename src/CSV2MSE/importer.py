import configparser
import csv
import os
import shutil
from tkinter import filedialog as fd
from typing import Iterable


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
        key: config["card"].get(key)
        for key in config["card"]
        if config["card"].get(key)
    }

    return metadata, columns


def create_set_dir(metadata: dict[str, str]) -> None:
    """
    Generate an empty set file for MSE 2.0 and add any set details from the metadata
    dictionary. Defaults to using the m15-altered stylesheet.
    """
    if not metadata.get("title"):
        metadata["title"] = "Untitled"

    os.mkdir(metadata["title"] + ".mse-set")

    with open(metadata["title"] + ".mse-set/set", "w") as f:
        f.write("mse_version: 2.0.0\n")
        f.write("game: magic\n")
        f.write("stylesheet: m15-altered\n")
        f.write("set_info:\n")
        for key in metadata:
            f.write(f"\t{key}: {metadata[key]}\n")


def read_csv() -> list[dict[str, str]]:
    """
    Prompt the user to select a CSV file, then import each line as a dictionary
    mapping the row's value to the column name."
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
                body.append({key: val for key, val in zip(header, row)})

    return body


def process_csv(columns: dict[str, str], cards: Iterable[dict[str, str]]) -> None:
    return


def zip_set_dir(metadata: dict[str, str]) -> None:
    """
    Take the directory containing the set file and zip it so that MSE can open it.
    """
    if not metadata.get("title"):
        metadata["title"] = "Untitled"

    shutil.make_archive(metadata["title"], "zip", metadata["title"] + ".mse-set")
    shutil.rmtree(metadata["title"] + ".mse-set")
    os.rename(metadata["title"] + ".zip", metadata["title"] + ".mse-set")


if __name__ == "__main__":
    config_file = "metadata.cfg"
    metadata, columns = read_config_file(config_file)

    # for testing
    try:
        shutil.rmtree(metadata["title"] + ".mse-set")
    except Exception:
        pass
    try:
        os.remove(metadata["title"] + ".mse-set")
    except Exception:
        pass

    create_set_dir(metadata)
    card_list = read_csv()
    process_csv(columns, card_list)
    zip_set_dir(metadata)
