#!/usr/bin/env bash

rm -rf dist build

pyinstaller --clean --onefile --windowed -F gui.py --icon=./quickdataload.ico --name QuickdataLoad \
  --add-data "m3_fields_info.db:." \
  --add-data "Mapping_Template.xlsx:inforion/excelexport/" \
  --add-data "quickdataload.ico:."
