This version of the game has been modified to allow for exporting to a .exe file.

Since applications packaged into .exe files unpack their contents into a temporary directory, it is not possible to save game progress using local files. Hence, this version creates and saves progress to a file in the AppData/Roaming directory.

It is for this reason that if intending to run the game through a python interpreter, it is recommended to use the standard version, as to prevent any unnecessary files being written to the home directory.