from os import path
import csv
import fileinput

class Save():
    def __init__(self):
        self.dir = path.dirname(path.dirname(path.abspath(__file__)))       # the bulk of this module is copied from
        self.dir = path.join(self.dir, "Assets")                            # the ATM project
        self.saveFile = path.join(self.dir, "savedata.csv")                 # load in save file csv

        with open(self.saveFile) as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
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