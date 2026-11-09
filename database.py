import csv
import os
import shutil
from datetime import datetime

FILENAME = "trading_journal.csv"
CONFIG_FILE = "config_capital.txt"
RECEIPTS_DIR = "receipts"
CHARTS_DIR = "charts"
BACKUP_DIR = "backup_data"

def get_initial_capital():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return float(f.read().strip())
        except ValueError:
            return 1000.0
    return 1000.0

def save_initial_capital(val):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(str(val))

def init_file():
    for d in [RECEIPTS_DIR, CHARTS_DIR, BACKUP_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
        
    if not os.path.exists(FILENAME):
        with open(FILENAME, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Symbol", "Action", "PnL (USD)", "Withdrawal (USD)", "RR Target", "Capital Unit", "Rule Status", "Notes", "Receipt", "Chart"])

def get_all_csv_rows():
    rows = []
    if os.path.exists(FILENAME):
        with open(FILENAME, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)
            rows = list(reader)
    return rows