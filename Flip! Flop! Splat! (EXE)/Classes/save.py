import os
from os import path
import csv
import fileinput

class Save():
    def __init__(self):
        self.dir = os.getenv("APPDATA")
        self.dir = path.join(self.dir, "Flip! Flop! Splat!")
        self.saveFile = path.join(self.dir, "savedata.csv")     # get absolute path to AppData/Roaming

        if not os.path.exists(self.dir):        # check if game directory in AppData exists, and
            os.mkdir(self.dir)                  # if not, create directory
        
        if os.path.isfile(self.saveFile):
            with open(self.saveFile) as csvfile:
                csvreader = csv.reader(csvfile, delimiter=',')      # check is save file exists and read it in
                line = 0
                for row in csvreader:
                    if line == 0:
                        line += 1
                    else:
                        self.username = str(row[0])     # assign variables to data read in from save file,
                        self.level = int(row[1])        # to make it easier to manipulate
                        self.kills = int(row[2])
                        self.deaths = int(row[3])
                        self.flips = int(row[4])
                        self.control = int(row[5])

        else:
            with open(self.saveFile, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Name", "Level", "Kills", "Deaths", "Flips", "Control"])       # if save file does not exist,
                writer.writerow(["noname", "1", "0", "0", "0", "0"])                            # create a new, blank save file

            self.newSave()
            self.username = "noname"
            self.control = 0

    def saveData(self):
        with fileinput.input(files=(self.saveFile), inplace=True, mode='r') as f:
            reader = csv.DictReader(f)
            print(",".join(reader.fieldnames))      # read file as dictionary

            for row in reader:
                row["Name"] = self.username     # print variables back to save file
                row["Level"] = self.level
                row["Kills"] = self.kills
                row["Deaths"] = self.deaths
                row["Flips"] = self.flips
                row["Control"] = self.control

                print(",".join([str(row["Name"]), str(row["Level"]), str(row["Kills"]), str(row["Deaths"]), str(row["Flips"]), 
                                str(row["Control"])]))

    def newSave(self):      # reset save file
        self.level = 1
        self.kills = 0
        self.deaths = 0
        self.flips = 0