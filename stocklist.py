from ftplib import FTP
import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}

# this is used to get all tickers from the market.


exportList = []

NON_COMMON_SECURITY_TYPES = (
    r"\bdepositary\b",
    r"\bpreferred\b",
    r"\bwarrants?\b",
    r"\bunits?\b",
    r"\bright[s]?\b",
    r"\bnotes?\b",
    r"\bdebentures?\b",
    r"\bbonds?\b",
    r"\bfunds?\b",
    r"\btrusts?\b",
)


class NasdaqController:
    def getList(self):
        return exportList

    def __init__(self, update=None):
        self.filenames = {
            "nasdaqlisted": "data/nasdaqlisted.txt",
        }

        if update is None:
            update = env_bool("UPDATE_TICKERS")

        if update:
            with FTP("ftp.nasdaqtrader.com") as ftp:
                ftp.login()
                ftp.cwd("SymbolDirectory")
                for filename, filepath in self.filenames.items():
                    with open(filepath, "wb") as output:
                        ftp.retrbinary("RETR " + filename + ".txt", output.write)

        global exportList
        exportList = []
        symbols = set()
        with Path("data/alllisted.txt").open("w") as all_listed:
            for filename, filepath in self.filenames.items():
                with open(filepath, "r") as file_reader:
                    next(file_reader, None)
                    for line in file_reader:
                        fields = line.strip().split("|")
                        if len(fields) < 2:
                            continue

                        symbol, security_name = fields[0].strip(), fields[1].strip()
                        is_etf = len(fields) > 6 and fields[6] == "Y"
                        is_test_issue = len(fields) > 3 and fields[3] == "Y"
                        is_non_common_security = any(
                            re.search(security_type, security_name.lower())
                            for security_type in NON_COMMON_SECURITY_TYPES
                        )
                        if (not symbol or not security_name or is_etf or
                                is_test_issue or is_non_common_security or
                                symbol in symbols):
                            continue

                        symbols.add(symbol)
                        exportList.append(symbol)
                        all_listed.write(symbol + "," + symbol + "|" + security_name + "\n")

if __name__ == "__main__":
    StocksController = NasdaqController()
    print(StocksController.getList())
    print("Refresh Done.")