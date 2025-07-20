# Excel to Database Ingestion Tool

## About
This is a Python script I wrote to automate the process of loading project data from Excel files into a SQLite database. I built it to practice data cleaning, ETL, and working with real-world file formats. It can be adapted for other databases or more complex schemas.

## Motivation
At my civil engineering company, we have lots of project data in Excel files. I wanted a repeatable way to centralize and analyze this data for reporting and analytics.

## How to Run
```bash
pip install pandas sqlalchemy openpyxl
python ingest.py
```

Place your Excel files in the `excel_files` folder.

## Future Improvements
- Add support for other file formats (CSV, Google Sheets)
- Add error handling and logging
- Make schema mapping more flexible
- Connect to PostgreSQL for production use
