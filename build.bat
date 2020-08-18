rm -rf dist build

pyinstaller --clean --win-private-assemblies -F gui.pyw --name QuickdataLoad --add-data "m3_fields_info.db;." --add-data "Mapping_Template.xlsx;inforion/excelexport/" --add-data "iconfinder.icns;."
