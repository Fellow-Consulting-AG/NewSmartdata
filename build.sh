#!/usr/bin/env bash
rm -rf dist build
pyinstaller --clean --noconsole --onefile --windowed -F gui.py --icon=iconfinder.icns --name Smartdata \
    --add-binary "m3_fields_info.db:." \
    --add-binary "Mapping_Template.xlsx:inforion/excelexport/" \
    --add-binary "iconfinder.icns:."
