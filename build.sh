#!/usr/bin/env bash
rm -rf dist build
pyinstaller --clean --noconsole --onefile --windowed -F gui.py --icon=iconfinder.icns --name Smartdata \
    --add-data "m3_fields_info.db:." \
    --add-data "Mapping_Template.xlsx:inforion/excelexport/" \
    --add-data "iconfinder.icns:."
