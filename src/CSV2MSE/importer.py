import configparser
import os


def read_config_file(file: str) -> tuple[dict[str, str], dict[str, str]]:
    """
    Read the configuration details given in the provided config file. Returns two
    dictionaries: one with metadata about the set, and one with mappings between
    the CSV file and the canonical MSE field names.
    """
    if not os.path.exists(file):
        raise OSError("Can't find metadata.cfg in working directory!")

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


def create_set_dir():
    return


def read_csv():
    contents = None
    return contents


def process_csv(dict):
    return


if __name__ == "__main__":
    # read config file
    config_file = "metadata.cfg"
    metadata, columns = read_config_file(config_file)
    print(metadata)
    print(columns)
    # initialize set directory and set file
    # read csv file
    # process csv file
