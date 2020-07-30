import inforion as infor
import pandas as pd
import PySimpleGUI as sg
from PySimpleGUI import B
from PySimpleGUI import Btn
from PySimpleGUI import Button
from PySimpleGUI import ButtonMenu
from PySimpleGUI import Canvas
from PySimpleGUI import CB
from PySimpleGUI import Check
from PySimpleGUI import Checkbox
from PySimpleGUI import Col
from PySimpleGUI import Column
from PySimpleGUI import Combo
from PySimpleGUI import FileBrowse
from PySimpleGUI import Frame
from PySimpleGUI import Graph
from PySimpleGUI import Image
from PySimpleGUI import In
from PySimpleGUI import Input
from PySimpleGUI import InputCombo
from PySimpleGUI import InputText
from PySimpleGUI import LBox
from PySimpleGUI import Listbox
from PySimpleGUI import Menu
from PySimpleGUI import ML
from PySimpleGUI import MLine
from PySimpleGUI import Multiline
from PySimpleGUI import OptionMenu
from PySimpleGUI import Output
from PySimpleGUI import Pane
from PySimpleGUI import ProgressBar
from PySimpleGUI import Radio
from PySimpleGUI import Sizer
from PySimpleGUI import Slider
from PySimpleGUI import Spin
from PySimpleGUI import StatusBar
from PySimpleGUI import T
from PySimpleGUI import Tab
from PySimpleGUI import TabGroup
from PySimpleGUI import Table
from PySimpleGUI import Text
from PySimpleGUI import Tree
from PySimpleGUI import TreeData
from PySimpleGUI import Txt
from PySimpleGUI import VerticalSeparator
from PySimpleGUI import Window

from _version import __version__
import validators

sg.theme("SystemDefault")
appFont = ("Helvetica", 13)
sg.set_options(font=appFont)
sg.theme("Topanga")


def show_main():

    METER_REASON_CANCELLED = "cancelled"
    # METER_REASON_CLOSED = "closed"
    # METER_REASON_REACHED_MAX = "finished"
    METER_OK = True
    # METER_STOPPED = False

    menu_def = [["File", ["Save", "Load", "Exit"]],
                ["Help", ["About", "Help"]]]

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
                                FileBrowse(file_types=("ION API File",
                                                       "*.ionapi")),
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

    window = sg.Window("M3 Import Data", layout, margins=(10, 10))

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
                sg.popup_quick_message("You have to provide a valid URL", keep_on_top=True, text_color='red', no_titlebar=True)
                METER_OK = False
            
            ionfile = values["-ION-FILE-"]
            if infor.filehandling.checkfile_exists(ionfile) !=True:
                sg.popup_quick_message("You have to provide a valid ionfile", keep_on_top=True, text_color='red', no_titlebar=True)
                METER_OK = False
                
            program = values["-ION-Program-"]
            if program.empty():
                sg.popup_quick_message("You have to provide a program", keep_on_top=True, text_color='red', no_titlebar=True)
                METER_OK = False
                
            method = values["-ION-METHOD-"]
            if method.empty():
                sg.popup_quick_message("You have to provide atleast one method", keep_on_top=True, text_color='red', no_titlebar=True)
                METER_OK = False
                
            inputfile = values["-INPUT-FILE-"]
            outputfile = values["-OUTPUT-FILE-"]
            if outputfile.empty():
                sg.popup_quick_message("You have to provide output file path", keep_on_top=True, text_color='red', no_titlebar=True)
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
            sg.popup_ok("Save")

        if event == "Load":
            sg.popup_ok("Load")

        if event == "Exit":
            window.close()

        if event == "About":
            open_about()

        if event == "Help":
            open_help()

    window.close()


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
    sg.popup_ok("NewSmartdata, Version: {}".format(__version__), about_text)


def open_help():
    sg.popup_ok("Help")


show_main()
