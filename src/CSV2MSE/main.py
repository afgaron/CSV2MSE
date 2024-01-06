import card_importer

if __name__ == "__main__":
    try:
        config_file = "metadata.cfg"
        metadata, columns = card_importer.read_config_file(config_file)
        set_dir = card_importer.create_set_dir(metadata)
        card_list = card_importer.read_csv()
        card_importer.process_csv(set_dir, columns, card_list)
        card_importer.zip_set_dir(set_dir)
    except Exception as e:
        print(e)
        input("Press any key to exit")
