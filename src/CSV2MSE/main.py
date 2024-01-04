import importer

if __name__ == "__main__":
    config_file = "metadata.cfg"
    metadata, columns = importer.read_config_file(config_file)
    set_dir = importer.create_set_dir(metadata)
    card_list = importer.read_csv()
    importer.process_csv(set_dir, columns, card_list)
    importer.zip_set_dir(set_dir)
