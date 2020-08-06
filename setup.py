from setuptools import setup

APP = ["gui.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": True,
    "iconfile": "iconfinder.icns",
    "plist": {
        "CFBundleShortVersionString": "0.2.0",
        "LSUIElement": True,
    },
    "packages": ["PySimpleGUI", "inforion", "pandas"],
}
setup(
    app=APP,
    name="NewSmartdata",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
    install_requires=["PySimpleGUI", "inforion", "pandas"],
)
