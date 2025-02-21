# CSV2MSE

CSV2MSE is a generic CSV to MSE importer that can convert (most) CSV files
into `.mse-set` files. Download it here: https://bit.ly/CSV2MSE_1_1

## Usage

First, extract the contents of the `CSV2MSE.zip` file. It contains two files: an
executable (`CSV2MSE.exe`) and a config file (`metadata.cfg`).

Open the config file in any text editor. It has two sections: `set_info` and `card`.
In the `set_info` section, fill in any information about your set you want to have
prepopulated in the set info menu in MSE. The value you enter for `title` will also be
used as the name of your `.mse-set` file.

In the `card` section, fill in the mapping between the MSE value names and the columns
of your CSV file. For example, if your file has a column called `mana_cost`, put that
in row 16:
```
casting_cost = mana_cost
```
For any rows in the `card` section that aren't filled in, the importer will assume
your CSV uses the same name for the matching column. Any columns in your CSV that aren't
listed in the config file will just be skipped.

Once the config file is filled in, you can run the executable file. (Make sure it's in
the same folder as the config file!) A pop-up will appear prompting you to select the
CSV you want to import. Assuming there are no errors, it will run for a few seconds and
then exit, creating the `.mse-set` file in the same folder.

## Advanced

The importer is also available as a Python script that can be run from the command line.
The entry point is `main.py`; the read and write operations are performed in
`card_importer.py`; and additional parsing and formatting functions to make data
MSE-compliant are defined in `card_parser.py`.

You are free to use and modify this code. If you have suggestions for improvements,
please reach out!
