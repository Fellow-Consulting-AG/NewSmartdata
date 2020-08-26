rm -rf dist build

pyinstaller --clean --windowed --onefile --icon=./quickdataload.ico -F gui.py --name QuickdataLoad --add-data "m3_fields_info.db;." --add-data "Mapping_Template.xlsx;inforion/excelexport/" --add-data "quickdataload.ico;."
