import ntpath
import os
import subprocess
import sys
import threading
from json import dump as jsondump
from json import load as jsonload
from pathlib import Path

import inforion as infor
import pandas as pd
import PySimpleGUI as sg
import validators
from inforion import excelexport
from inforion.transformation.transform import parallelize_tranformation
from PySimpleGUI import Button
from PySimpleGUI import Column
from PySimpleGUI import FileBrowse
from PySimpleGUI import Frame
from PySimpleGUI import Input
from PySimpleGUI import Text

from _version import __version__
from programs import programs

dir = str(Path.home()) + "/.QuickdataLoad"
if not os.path.exists(dir):
    os.makedirs(dir)
os.chdir(dir)  # just for safety

ntpath.basename("a/b/c")

sg.theme("SystemDefault")
appFont = ("Helvetica", 13)
sg.set_options(font=appFont)
sg.theme("LightGreen")
sg.ChangeLookAndFeel("LightGreen")

SETTINGS_FILE = os.path.join(dir, "settings.json")

DEFAULT_SETTINGS = {
    "ion_file": None,
    "m3_company": 0,
    "m3_div": "",
    "url": "",
    "method": "",
    "input_file": "",
    "output_file": "",
    "start": 0,
    "end": None,
}
SETTINGS_KEYS_TO_ELEMENT_KEYS = {
    "ion_file": "-ION-FILE-",
    "m3_company": "-M3-COMPANY-",
    "m3_div": "-M3-DIV-",
    "url": "-ION-URL-",
    "method": "-ION-METHOD-",
    "input_file": "-INPUT-FILE-",
    "output_file": "-OUTPUT-FILE-",
    "start": "-ION-BEGIN-",
    "end": "-ION-END-",
}

root = os.path.dirname(__file__)
if getattr(sys, "_MEIPASS", False):
    root = getattr(sys, "_MEIPASS")
icon_image = os.path.join(root, "quickdataload.ico")


def show_main():
    METER_REASON_CANCELLED = "cancelled"
    # METER_REASON_CLOSED = "closed"
    # METER_REASON_REACHED_MAX = "finished"
    METER_OK = True
    # METER_STOPPED = False

    menu_def = [
        # ["File", ["Save", "Load", "Exit"]],
        ["File", ["Exit"]],
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
                    [[
                        Text(),
                        Column([
                            [
                                Text("ION File:", size=(14, 1)),
                                Input(key="-ION-FILE-"),
                                FileBrowse(),
                            ],
                            [
                                Text("M3 Company/Div:"),
                                Input(key="-M3-COMPANY-", size=(5, 1)),
                                Input(key="-M3-DIV-", size=(7, 1)),
                            ],
                        ]),
                    ]],
                )
            ],
            # Information frame
            [
                Frame(
                    "Input Data",
                    [[
                        Text(),
                        Column([
                            [
                                Text("URL:", size=(14, 1)),
                                Input(key="-ION-URL-"),
                            ],
                            [
                                Text("Program:", size=(14, 1)),
                                sg.Input(
                                    size=(10, 1),
                                    enable_events=True,
                                    key="-ION-FILTER-",
                                ),
                            ],
                            [
                                Text(justification="r", size=(14, 1)),
                                sg.Listbox(
                                    programs,
                                    size=(10, 5),
                                    enable_events=False,
                                    key="-ION-Program-",
                                    select_mode="single",
                                ),
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
                        ], ),
                    ]],
                )
            ],
        ], )

    layout = [
        [sg.Menu(menu_def, tearoff=True, pad=(200, 1))],
        [col1],
        [Button("Execute"), Button("Cancel")],
    ]

    window = sg.Window("QuickdataLoad - Main",
                       layout=layout,
                       icon=icon_image,
                       margins=(10, 10))
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

        if values["-ION-FILTER-"] != "":
            search = values["-ION-FILTER-"]
            filtered_programs = [x for x in programs if search in x]
            window["-ION-Program-"].update(filtered_programs)
        else:
            window["-ION-Program-"].update(programs)

        if event == "Execute":

            url = values["-ION-URL-"]
            ionfile = values["-ION-FILE-"]
            programs_list = values["-ION-Program-"]
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

            if validators.url(url) != True:
                sg.popup_quick_message(
                    "You have to provide a valid URL",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )
                METER_OK = False
            elif infor.filehandling.checkfile_exists(ionfile) != True:
                sg.popup_quick_message(
                    "You have to provide a valid ionfile",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )
                METER_OK = False
            elif not programs_list:
                sg.popup_quick_message(
                    "You have to provide a program",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )
                METER_OK = False
            elif not method:
                sg.popup_quick_message(
                    "You have to provide atleast one method",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )
                METER_OK = False
            elif not outputfile:
                sg.popup_quick_message(
                    "You have to provide output file path",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )
                METER_OK = False
            elif not infor.filehandling.checkfile_exists(inputfile):
                sg.popup_quick_message(
                    "Input File not found",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )
                METER_OK = False
            elif end is not None and end < start:
                sg.popup_quick_message(
                    "Begin value must be greater then End value",
                    keep_on_top=True,
                    text_color="red",
                    no_titlebar=True,
                )
                METER_OK = False
            else:
                METER_OK = True
                dataframe = pd.read_excel(inputfile, dtype=str)
                program = programs_list[0]

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
                return sg.Text(text + ":", justification="r", size=(12, 1))

            column = Column([
                [
                    Frame(
                        "Input Data",
                        [[
                            Text(),
                            Column([
                                [
                                    TextLabel("Program"),
                                    sg.Input(
                                        size=(10, 1),
                                        enable_events=True,
                                        key="-FILTER-",
                                    ),
                                ],
                                [
                                    Text(justification="r", size=(12, 1)),
                                    sg.Listbox(
                                        programs,
                                        size=(10, 5),
                                        enable_events=False,
                                        key="-PROGRAM-",
                                        select_mode="multiple",
                                    ),
                                ],
                                [
                                    TextLabel("Output Folder"),
                                    sg.Input(key="-OUTPUT-FOLDER-"),
                                    sg.FolderBrowse(target="-OUTPUT-FOLDER-"),
                                ],
                            ], ),
                        ]],
                    )
                ],
            ], )

            layout_extract = [[column], [Button("Execute"), Button("Cancel")]]
            window_extract = sg.Window(
                "QuickdataLoad  - Extract",
                layout=layout_extract,
                icon=icon_image,
                margins=(10, 10),
            )

            while True:
                event, values = window_extract.read()

                if event == sg.WIN_CLOSED or event == "Cancel":
                    window_extract.Close()
                    window_extract_active = False
                    break

                if values["-FILTER-"] != "":
                    search = values["-FILTER-"]
                    filtered_programs = [x for x in programs if search in x]
                    window_extract["-PROGRAM-"].update(filtered_programs)
                else:
                    window_extract["-PROGRAM-"].update(programs)

                if event == "Execute":
                    try:
                        programs_list = values["-PROGRAM-"]
                        output_folder = values["-OUTPUT-FOLDER-"]

                        if validators.length(programs_list,
                                             1) and validators.length(
                                                 output_folder, 1):
                            for program in programs_list:
                                output_path = output_folder + os.sep + program
                                excelexport.generate_api_template_file(
                                    program, output_path)
                            sg.popup("Template(s) generated!", icon=icon_image)
                        else:
                            sg.popup_ok("Please, check the form values!",
                                        icon=icon_image)
                    except Exception as e:
                        infor.logger.exception(e)
                        sg.popup_ok(
                            "Something went wrong! Please check the error logs!",
                            icon=icon_image,
                        )

        if event == "Transform" and not window_extract_active:

            window_transform_active = True
            window.Hide()

            def TextLabel(text):
                return sg.Text(text + ":", justification="r", size=(15, 1))

            column = Column([
                [
                    Frame(
                        "Input Data",
                        [[
                            Text(),
                            Column([
                                [
                                    TextLabel("Mapping File"),
                                    Input(key="-MAPPING-FILE-"),
                                    FileBrowse(),
                                ],
                                [
                                    TextLabel("Main Sheet"),
                                    Input(key="-MAIN-SHEET-"),
                                ],
                                [
                                    TextLabel("Input File"),
                                    Input(key="-INPUT-FILE-"),
                                    FileBrowse(),
                                ],
                                [
                                    TextLabel("Output Folder"),
                                    sg.Input(key="-OUTPUT-FOLDER-"),
                                    sg.FolderBrowse(target="-OUTPUT-FOLDER-"),
                                ],
                            ], ),
                        ]],
                    )
                ],
            ], )

            layout_transform = [[column],
                                [Button("Execute"),
                                 Button("Cancel")]]
            window_transform = sg.Window(
                "QuickdataLoad  - Transform",
                icon=icon_image,
                layout=layout_transform,
                margins=(10, 10),
            )

            thread_transform = None
            while True:
                event, values = window_transform.read()

                if event == sg.WIN_CLOSED or event == "Cancel":
                    window_transform.Close()
                    window_transform_active = False
                    break

                elif event == "Transform_End":
                    sg.popup("Transformation ended", icon=icon_image)
                    if thread_transform is not None:
                        thread_transform.join(timeout=0)
                        thread_transform = None

                if event == "Execute":

                    try:
                        mapping_file = values["-MAPPING-FILE-"]
                        main_sheet = values["-MAIN-SHEET-"]
                        input_file = values["-INPUT-FILE-"]
                        output_folder = values["-OUTPUT-FOLDER-"]

                        if (validators.length(mapping_file, 1)
                                and validators.length(main_sheet, 1)
                                and validators.length(input_file, 1)
                                and validators.length(output_folder, 1)):

                            output_file_name = "output_" + path_leaf(
                                input_file)
                            output_file = output_folder + os.sep + output_file_name
                            thread_transform = threading.Thread(
                                target=transform,
                                args=(
                                    mapping_file,
                                    main_sheet,
                                    input_file,
                                    output_file,
                                    window_transform,
                                ),
                            )
                            thread_transform.start()
                            sg.popup(
                                "Transformation file result will generated at: \n"
                                + output_file,
                                icon=icon_image,
                            )
                        else:
                            sg.popup_ok("Please, check the form values!",
                                        icon=icon_image)
                    except Exception as e:
                        infor.logger.exception(e)
                        sg.popup_ok(
                            "Something went wrong! Please check the error logs!",
                            icon=icon_image,
                        )

        window.UnHide()

    window.close()


def transform(mapping_file, main_sheet, input_file, output_file, win):
    input_data = pd.read_excel(input_file, dtype=str)
    parallelize_tranformation(mapping_file,
                              main_sheet,
                              input_data,
                              output_file,
                              n_cores=1)
    # TODO - Use a Queue to notify GUI
    # win.write_event_value("Transform_End", "Transformed file generated at: \n" + output_file)


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def on_progress(total, processed):
    sg.one_line_progress_meter("My 1-line progress meter", processed, total,
                               "single")


def open_about():
    about_text = """
    Fellow Consulting AG
    Address: Anzinger Str. 21 A, 85586 Poing, Germany
    Tel: +49 (0)8121 792980
    Email: sales@fellow-consulting.de
    """
    sg.popup_ok("QuickdataLoad, Version: {}".format(__version__),
                about_text,
                icon=icon_image)


def open_help():
    try:
        docs = "https://new-QuickdataLoad-tool-fur-infor.readthedocs.io/"
        command = None
        if sys.platform.startswith("linux"):
            command = "/usr/bin/google-chrome-stable {}".format(docs)
        elif sys.platform.startswith("darwin"):
            command = "/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome {}".format(
                docs)
        elif sys.platform.startswith("win"):
            command = "start chrome {}".format(docs)
        subprocess.Popen(command,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    except Exception as e:
        sg.popup("Cannot open browser.", icon=icon_image)


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
                print(
                    f"Problem updating settings from window values. Key = {key}"
                )

    with open(settings_file, "w") as f:
        jsondump(settings, f)

    if notify:
        sg.popup("Settings saved", icon=icon_image)


if __name__ == "__main__":
    show_main()
