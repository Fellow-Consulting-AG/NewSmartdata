#!/usr/bin/env bash

rm -rf dist build

pyinstaller --clean --noconsole --onefile --windowed -F gui.pyw --icon=iconfinder.icns --name QuickdataLoad \
  --add-data "m3_fields_info.db:." \
  --add-data "Mapping_Template.xlsx:inforion/excelexport/" \
  --add-data "iconfinder.icns:."
