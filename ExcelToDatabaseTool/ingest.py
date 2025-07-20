"""
Quick-and-simple Excel -> SQLite ingester (personal learning).
Drops any .xlsx files from ./excel_files into a 'projects' table.
For a more robust version with upserts/normalization, see ../ingest_projects.py
"""

import os
import pandas as pd
from sqlalchemy import create_engine

EXCEL_DIR = 'excel_files'
DB_URL = 'sqlite:///projects.db'

def main():
    # create folder if it doesn't exist, so it's obvious where to drop files
    os.makedirs(EXCEL_DIR, exist_ok=True)
    engine = create_engine(DB_URL)
    files = [f for f in os.listdir(EXCEL_DIR) if f.lower().endswith('.xlsx')]
    if not files:
        print(f"No Excel files found in '{EXCEL_DIR}'. Place .xlsx files there and re-run.")
        return
    for fname in files:
        path = os.path.join(EXCEL_DIR, fname)
        try:
            df = pd.read_excel(path)
            df.to_sql('projects', engine, if_exists='append', index=False)
            print(f"Imported {len(df)} rows from {fname}")
        except Exception as e:
            print(f"Failed to import {fname}: {e}")

if __name__ == '__main__':
    main()
