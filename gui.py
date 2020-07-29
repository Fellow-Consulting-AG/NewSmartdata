from json import dump as jsondump
from json import load as jsonload
from os import path

import inforion as infor
import pandas as pd
import PySimpleGUI as sg
from _version import __version__
from PySimpleGUI import (CB, ML, B, Btn, Button, ButtonMenu, Canvas, Check,
                         Checkbox, Col, Column, Combo, FileBrowse, Frame,
                         Graph, Image, In, Input, InputCombo, InputText, LBox,
                         Listbox, Menu, MLine, Multiline, OptionMenu, Output,
                         Pane, ProgressBar, Radio, Sizer, Slider, Spin,
                         StatusBar, T, Tab, TabGroup, Table, Text, Tree,
                         TreeData, Txt, VerticalSeparator, Window)

sg.theme("SystemDefault")
appFont = ("Helvetica", 13)
sg.set_options(font=appFont)
sg.theme("Topanga")


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

    menu_def = [["File", ["Save", "Load", "Exit"]], ["Help", ["About", "Help"]]]

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

    window = sg.Window("M3 Import Data", layout, margins=(10, 10))
    settings = load_settings(SETTINGS_FILE, DEFAULT_SETTINGS)

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
            ionfile = values["-ION-FILE-"]
            program = values["-ION-Program-"]
            method = values["-ION-METHOD-"]
            inputfile = values["-INPUT-FILE-"]
            outputfile = values["-OUTPUT-FILE-"]
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
            save_settings(SETTINGS_FILE, settings, values)

        if event == "Load":
            settings = load_settings(SETTINGS_FILE, DEFAULT_SETTINGS)
            fill_form_with_settings(window, settings)

        if event == "About":
            open_about()

        if event == "Help":
            open_help()

        if event in (sg.WIN_CLOSED, "Exit"):
            break

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
    sg.popup_ok("NewSmartdata, Version: {}".format(__version__), about_text)


def open_help():
    sg.popup_ok("Help")


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
        save_settings(settings_file, settings, None)
    return settings


def save_settings(settings_file, settings, values):
    if values:
        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:
            try:
                settings[key] = values[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]]
            except Exception as e:
                print(f"Problem updating settings from window values. Key = {key}")

    with open(settings_file, "w") as f:
        jsondump(settings, f)

    sg.popup("Settings saved")


show_main()
