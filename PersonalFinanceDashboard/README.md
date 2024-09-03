# Personal Finance Dashboard 💰

A Flask web application for tracking personal expenses, categorizing transactions, and visualizing spending patterns. Started this as a weekend project to get my own finances organized - figured I'd share it since it turned out pretty useful!

## What it does

- **📊 Interactive Dashboard** - Shows your spending overview with some nice charts
- **📁 CSV Upload** - Import bank statements (took forever to get all the different formats working)
- **🏷️ Smart Categorization** - Automatically sorts transactions (groceries, gas, etc.)
- **📈 Data Visualization** - Monthly trends and breakdowns using Chart.js
- **🔍 Transaction Filtering** - Search and filter by dates, categories
- **💾 SQLite Database** - Keeps everything stored locally
- **📱 Responsive Design** - Works on phone/tablet (mostly)

## Screenshots

### Dashboard
![Dashboard showing spending overview and charts]
(Screenshots to be added - need to figure out how to do this without exposing real data)

### Upload Page  
![CSV upload interface with drag-and-drop]

### Transactions
![Filterable transaction history table]

## How to run it

1. **Install the stuff:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Start it up:**
   ```powershell
   python app.py
   ```

3. **Check it out:**
   Go to `http://localhost:5001` in your browser

4. **Upload some data:**
   - Hit the "Upload Bank Data" button
   - Drag your CSV file or click to browse  
   - App should figure out the format automatically (tested with Chase, BofA, a few others)

## CSV Format 

The app tries to auto-detect bank formats but your CSV needs these columns (can be named different things):

- **Date:** Date, Transaction Date, Posted Date, etc.
- **Description:** Description, Memo, Transaction, etc.
- **Amount:** Amount, Debit, Credit, etc.

### Example:
```csv
Date,Description,Amount
2024-01-15,"GROCERY STORE",-85.42
2024-01-14,"PAYCHECK DEPOSIT",2500.00
```

Works with most bank exports I've tried. If it doesn't work with yours, let me know and I can probably add support.

## What I learned building this

This started as a simple expense tracker but grew into something more useful. Here's the interesting stuff:

### Auto-categorization
Uses keyword matching to sort transactions. Not super smart but works pretty well:
- **Groceries:** looks for "grocery", "walmart", "target", etc.
- **Gas:** "shell", "exxon", "chevron", etc.  
- **Restaurants:** "starbucks", "mcdonalds", "pizza", etc.

Could probably use machine learning for this but keywords work fine for now.

### Technical stuff
- **Backend:** Flask with SQLite (keeps it simple)
- **Frontend:** Just HTML/CSS/JavaScript with Chart.js for graphs
- **Data processing:** pandas for CSV handling
- **Security:** Basic stuff like file validation, parameterized SQL queries

### File structure
```
PersonalFinanceDashboard/
├── app.py                 # Main Flask app
├── requirements.txt       # Dependencies  
├── README.md             # This file
├── sample_data.csv       # Test data
├── templates/            # HTML templates
│   ├── dashboard.html    # Main page
│   ├── upload.html       # File upload
│   └── transactions.html # Transaction list
├── uploads/              # Uploaded files (created automatically)
└── finance.db           # SQLite database (created automatically)
```

## Things I want to add

- Budget tracking and alerts
- Better categorization (maybe ML?)
- Recurring transaction detection  
- PDF export for reports
- Multi-account support
- Maybe API integration with banks (Plaid?)

## Notes

Built this mainly for myself but figured others might find it useful. Not production-ready - just a learning project that actually works pretty well. 

Feel free to fork it or suggest improvements!
