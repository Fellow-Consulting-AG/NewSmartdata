from distutils.core import setup
import py2exe

setup(
	windows=[{
		"script": "gui.py",
		# "icon_resources": [(1, "icon.ico")],
	}],
	options={
		"py2exe": {
			"unbuffered": True,
			"optimize": 1,
			"dist_dir": "installer/files",
		}
	},
)
