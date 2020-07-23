import PySimpleGUI as sg
from PySimpleGUI import FileBrowse, InputCombo, Combo, Multiline, ML, MLine, Checkbox, CB, Check, Button, B, Btn, ButtonMenu, Canvas, Column, Col, Combo, Frame, Graph, Image, InputText, Input, In, Listbox, LBox, Menu, Multiline, ML, MLine, OptionMenu, Output, Pane, ProgressBar, Radio, Slider, Spin, StatusBar, Tab, TabGroup, Table, Text, Txt, T, Tree, TreeData,  VerticalSeparator, Window, Sizer
import pandas as pd

import inforion as infor

sg.theme("SystemDefault")
appFont = ("Helvetica", 13)
sg.set_options(font=appFont)
sg.theme('Topanga')

def show_main():

    METER_REASON_CANCELLED = "cancelled"
    # METER_REASON_CLOSED = "closed"
    # METER_REASON_REACHED_MAX = "finished"
    METER_OK = True
    # METER_STOPPED = False

    menu_def = [['File', ['Open', 'Save', 'Exit', 'Properties']],
                ['Help', 'About...'],]      

    col1 = Column([
    # Logon frame
    [Frame('Logon information', [[Text(), Column([[Text('ION File:', size=(14,1)), Input(key='-ION-FILE-'), FileBrowse(file_types=("ION API File","*.ionapi"))], 
                                                  [Text('M3 Company/Div:'), Input(key='-M3-COMPANY-', size=(5,1)), Input(key='-M3-DIV-',size=(7,1))], ])]])],
    # Information frame
    [Frame('Input Data', [[Text(), Column([[Text('URL:', size=(14,1)), Input(key='-ION-URL-')],
                                     [Text('Program:', size=(14,1)), Input(key='-ION-Program-')],
                                     [Text('Method:', size=(14,1)), Input(key='-ION-METHOD-')],
                                     [Text('Input File:', size=(14,1)), Input(key='-INPUT-FILE-'), FileBrowse()],
                                     [Text('Output File:', size=(14,1)), Input(key='-OUTPUT-FILE-'), FileBrowse()],
                                     [Text('Begin on line:', size=(14,1)), Input(key='-ION-BEGIN-', enable_events=True)],
                                     [Text('End on line:', size=(14,1)), Input(key='-ION-END-', enable_events=True)], 
                                     ], )]])], ], )


    layout = [
        [sg.Menu(menu_def, tearoff=True, pad=(200, 1))],  
        [col1], [Button("Execute"), Button("Cancel")]]

    window = sg.Window("M3 Import Data", layout, margins=(10, 10))

    while True:  # Event Loop
        event, values = window.read()
        if event in (None, sg.WIN_CLOSED, "Cancel"):
            break

        if event in ("-ION-BEGIN-", "-ION-END-"):
            if values[event] and values[event][-1] not in ("0123456789"):
                sg.popup_quick_message("Please enter a valid row number", keep_on_top=True, text_color='red', no_titlebar=True)
        
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
                sg.popup_quick_message("Input File not found", keep_on_top=True, text_color='red', no_titlebar=True)
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

    window.close()


def on_progress(total, processed):
    sg.one_line_progress_meter("My 1-line progress meter", processed, total, "single")


show_main()
