# A simple setup script to create an executable using PyQt4. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# PyQt4app.py is a very simple type of PyQt4 application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

application_title = "Ghost" #what you want to application to be called
main_python_file = "game.py" #the name of the python file you use to run the program

import sys

from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

includes = ["atexit","re"]
include_files = ['assets/', 'options.json']

setup(
        name = application_title,
        version = "0.1",
        description = "An excellent game",
        options = {"build_exe" : {"includes" : includes, 'include_files':include_files }},
        executables = [Executable(main_python_file, base = base, icon = 'Ghost.ico')])
