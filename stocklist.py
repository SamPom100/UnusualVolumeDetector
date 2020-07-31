from ftplib import FTP
import os
import errno

exportList = []


class NasdaqController:
    def getList(self):
        return exportList

    def __init__(self, update=True):

        self.filenames = {
            "otherlisted": "data/otherlisted.txt",
            "nasdaqlisted": "data/nasdaqlisted.txt"
        }

        # Update lists only if update = True

        if update == True:
            self.ftp = FTP("ftp.nasdaqtrader.com")
            self.ftp.login()

            #print("Nasdaq Controller: Welcome message: " + self.ftp.getwelcome())

            self.ftp.cwd("SymbolDirectory")

            for filename, filepath in self.filenames.items():
                if not os.path.exists(os.path.dirname(filepath)):
                    try:
                        os.makedirs(os.path.dirname(filepath))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise

                self.ftp.retrbinary("RETR " + filename +
                                    ".txt", open(filepath, 'wb').write)

        all_listed = open("data/alllisted.txt", 'w')

        for filename, filepath in self.filenames.items():
            with open(filepath, "r") as file_reader:
                for i, line in enumerate(file_reader, 0):
                    if i == 0:
                        continue

                    line = line.strip().split("|")

                    if line[0] == "" or line[1] == "":
                        continue

                    all_listed.write(line[0] + ",")
                    global exportList
                    exportList.append(line[0])
                    all_listed.write(line[0] + "|" + line[1] + "\n")
