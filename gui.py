import os
import subprocess
import sys
from json import dump as jsondump
from json import load as jsonload
from os import path

import inforion as infor
import pandas as pd
import PySimpleGUI as sg
import validators
from inforion import excelexport
from PySimpleGUI import Button
from PySimpleGUI import Column
from PySimpleGUI import FileBrowse
from PySimpleGUI import Frame
from PySimpleGUI import Input
from PySimpleGUI import Text

from _version import __version__
from programs import programs


sg.theme("SystemDefault")
appFont = ("Helvetica", 13)
sg.set_options(font=appFont)
sg.theme("LightGreen")
sg.ChangeLookAndFeel("LightGreen")

SETTINGS_FILE = path.join(path.dirname(__file__), r"settings.json")
DEFAULT_SETTINGS = {"ion_file": None, "m3_company": 0, "m3_div": 0}
SETTINGS_KEYS_TO_ELEMENT_KEYS = {
    "ion_file": "-ION-FILE-",
    "m3_company": "-M3-COMPANY-",
    "m3_div": "-M3-DIV-",
}


def show_main():
    METER_REASON_CANCELLED = "cancelled"
    # METER_REASON_CLOSED = "closed"
    # METER_REASON_REACHED_MAX = "finished"
    METER_OK = True
    # METER_STOPPED = False

    menu_def = [
        ["File", ["Save", "Load", "Exit"]],
        [
            "Commands",
            [
                "Extract",
                "Load",
                "Merge",
                "Catalog",
                ["Get", "List", "Purge", "Upload"],
                "Transform",
            ],
        ],
        ["Help", ["About", "Help"]],
    ]

    col1 = Column(
        [
            # Logon frame
            [
                Frame(
                    "Logon information",
                    [
                        [
                            Text(),
                            Column(
                                [
                                    [
                                        Text("ION File:", size=(14, 1)),
                                        Input(key="-ION-FILE-"),
                                        FileBrowse(
                                            file_types=("ION API File", "*.ionapi")
                                        ),
                                    ],
                                    [
                                        Text("M3 Company/Div:"),
                                        Input(key="-M3-COMPANY-", size=(5, 1)),
                                        Input(key="-M3-DIV-", size=(7, 1)),
                                    ],
                                ]
                            ),
                        ]
                    ],
                )
            ],
            # Information frame
            [
                Frame(
                    "Input Data",
                    [
                        [
                            Text(),
                            Column(
                                [
                                    [
                                        Text("URL:", size=(14, 1)),
                                        Input(key="-ION-URL-"),
                                    ],
                                    [
                                        Text("Program:", size=(14, 1)),
                                        Input(key="-ION-Program-"),
                                    ],
                                    [
                                        Text("Method:", size=(14, 1)),
                                        Input(key="-ION-METHOD-"),
                                    ],
                                    [
                                        Text("Input File:", size=(14, 1)),
                                        Input(key="-INPUT-FILE-"),
                                        FileBrowse(),
                                    ],
                                    [
                                        Text("Output File:", size=(14, 1)),
                                        Input(key="-OUTPUT-FILE-"),
                                        FileBrowse(),
                                    ],
                                    [
                                        Text("Begin on line:", size=(14, 1)),
                                        Input(key="-ION-BEGIN-", enable_events=True),
                                    ],
                                    [
                                        Text("End on line:", size=(14, 1)),
                                        Input(key="-ION-END-", enable_events=True),
                                    ],
                                ],
                            ),
                        ]
                    ],
                )
            ],
        ],
    )

    layout = [
        [sg.Menu(menu_def, tearoff=True, pad=(200, 1))],
        [col1],
        [Button("Execute"), Button("Cancel")],
    ]

    window = sg.Window("SmartData - Main", layout, margins=(10, 10))
    settings = load_settings(SETTINGS_FILE, DEFAULT_SETTINGS)

    window_extract_active = False

    # Event Loop
    while True:
        event, values = window.read()
        if event in (None, sg.WIN_CLOSED, "Cancel"):
            break

        if event in ("-ION-BEGIN-", "-ION-END-"):
            if values[event] and values[event][-1] not in ("0123456789"):
                sg.popup_quick_message(
                    "Please enter a valid row number",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )

        if event == "Execute":

            url = values["-ION-URL-"]
            if validators.url(url) != True:
                sg.popup_quick_message(
                    "You have to provide a valid URL",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )
                METER_OK = False

            ionfile = values["-ION-FILE-"]
            if infor.filehandling.checkfile_exists(ionfile) != True:
                sg.popup_quick_message(
                    "You have to provide a valid ionfile",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )
                METER_OK = False

            program = values["-ION-Program-"]
            if program.empty():
                sg.popup_quick_message(
                    "You have to provide a program",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )
                METER_OK = False

            method = values["-ION-METHOD-"]
            if method.empty():
                sg.popup_quick_message(
                    "You have to provide atleast one method",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )
                METER_OK = False

            inputfile = values["-INPUT-FILE-"]
            outputfile = values["-OUTPUT-FILE-"]
            if outputfile.empty():
                sg.popup_quick_message(
                    "You have to provide output file path",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )
                METER_OK = False

            if values["-ION-BEGIN-"]:
                start = int(values["-ION-BEGIN-"])
            else:
                start = 0

            if values["-ION-END-"]:
                end = int(values["-ION-END-"])
            else:
                end = None

            if infor.filehandling.checkfile_exists(inputfile):
                dataframe = pd.read_excel(inputfile, dtype=str)
            else:
                sg.popup_quick_message(
                    "Input File not found",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )
                METER_OK = False

            if METER_OK:
                infor.main_load(
                    url,
                    ionfile,
                    program,
                    method,
                    dataframe,
                    outputfile,
                    start,
                    end,
                    on_progress,
                )

        if event == "Save":
            save_settings(True, SETTINGS_FILE, settings, values)

        if event == "Load":
            settings = load_settings(SETTINGS_FILE, DEFAULT_SETTINGS)
            fill_form_with_settings(window, settings)

        if event == "About":
            open_about()

        if event == "Help":
            open_help()

        if event in (sg.WIN_CLOSED, "Exit"):
            break

        # Command Windows

        if event == "Extract" and not window_extract_active:
            window_extract_active = True
            window.Hide()

            def TextLabel(text):
                return sg.Text(text + ":", justification="r", size=(15, 1))

            column = Column(
                [
                    [
                        Frame(
                            "Input Data",
                            [
                                [
                                    Text(),
                                    Column(
                                        [
                                            [
                                                TextLabel("Program"),
                                                sg.Listbox(
                                                    programs,
                                                    size=(10, 5),
                                                    key="-PROGRAM-",
                                                    select_mode="extended",
                                                ),
                                            ],
                                            [
                                                TextLabel("Output Folder"),
                                                sg.Input(key="-OUTPUT-FOLDER-"),
                                                sg.FolderBrowse(
                                                    target="-OUTPUT-FOLDER-"
                                                ),
                                            ],
                                        ],
                                    ),
                                ]
                            ],
                        )
                    ],
                ],
            )

            layout_extract = [[column], [Button("Execute"), Button("Cancel")]]
            window_extract = sg.Window(
                "SmartData  - Extract", layout_extract, margins=(10, 10)
            )

            while True:
                event, values = window_extract.read()

                if event == sg.WIN_CLOSED or event == "Cancel":
                    window_extract.Close()
                    window_extract_active = False
                    break

                if event == "Execute":
                    programs_list = values["-PROGRAM-"]
                    output_folder = values["-OUTPUT-FOLDER-"]

                    if validators.length(programs, 1) and validators.length(
                        output_folder, 1
                    ):
                        for program in programs_list:
                            output_path = output_folder + os.sep + program
                            excelexport.generate_api_template_file(program, output_path)
                        sg.popup("Template(s) generated!")
                    else:
                        sg.popup_ok("Please, check the form values!")

        window.UnHide()

    window.close()


def on_progress(total, processed):
    sg.one_line_progress_meter("My 1-line progress meter", processed, total, "single")


def open_about():
    about_text = """
    Fellow Consulting AG
    Address: Anzinger Str. 21 A, 85586 Poing, Germany
    Tel: +49 (0)8121 792980
    Email: sales@fellow-consulting.de
    """
    sg.popup_ok("SmartData, Version: {}".format(__version__), about_text)


def open_help():
    try:
        docs = "https://new-smartdata-tool-fur-infor.readthedocs.io/"
        command = None
        if sys.platform.startswith("linux"):
            command = "/usr/bin/google-chrome-stable {}".format(docs)
        elif sys.platform.startswith("darwin"):
            command = "/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome {}".format(
                docs
            )
        elif sys.platform.startswith("win"):
            command = "start chrome {}".format(docs)
        subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except Exception as e:
        sg.popup("Cannot open browser.")


def fill_form_with_settings(window, settings):
    if settings is None:
        settings = DEFAULT_SETTINGS
    for key, value in SETTINGS_KEYS_TO_ELEMENT_KEYS.items():
        window[value].update(settings[key])


def load_settings(settings_file, default_settings):
    try:
        with open(settings_file, "r") as f:
            settings = jsonload(f)
    except Exception as e:
        settings = default_settings
        save_settings(False, settings_file, settings, None)
    return settings


def save_settings(notify, settings_file, settings, values):
    if values:
        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:
            try:
                settings[key] = values[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]]
            except Exception as e:
                print(f"Problem updating settings from window values. Key = {key}")

    with open(settings_file, "w") as f:
        jsondump(settings, f)

    if notify:
        sg.popup("Settings saved")


show_main()
