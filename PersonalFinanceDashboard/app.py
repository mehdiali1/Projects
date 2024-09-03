"""
Personal Finance Dashboard
A Flask web app for tracking expenses, categorizing transactions, and visualizing spending patterns.

Features:
- Upload CSV bank statements
- Automatic expense categorization
- Interactive charts and reports
- Monthly/yearly analysis
- Budget tracking
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import sqlite3
from werkzeug.utils import secure_filename
import re

app = Flask(__name__)
app.secret_key = 'dev-secret-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database setup
def init_db():
    conn = sqlite3.connect('finance.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            account TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            keywords TEXT,
            color TEXT DEFAULT '#3498db'
        )
    ''')
    
    # Insert default categories
    default_categories = [
        ('Groceries', 'grocery,food,market,walmart,target,kroger', '#e74c3c'),
        ('Gas & Transportation', 'gas,fuel,uber,lyft,taxi,bus,metro', '#f39c12'),
        ('Restaurants', 'restaurant,cafe,starbucks,mcdonalds,pizza', '#e67e22'),
        ('Entertainment', 'movie,netflix,spotify,game,concert', '#9b59b6'),
        ('Utilities', 'electric,water,internet,phone,cable', '#34495e'),
        ('Shopping', 'amazon,clothing,electronics,mall', '#16a085'),
        ('Healthcare', 'doctor,pharmacy,hospital,dental', '#27ae60'),
        ('Income', 'salary,paycheck,deposit,transfer', '#2ecc71'),
        ('Other', '', '#95a5a6')
    ]
    
    for cat, keywords, color in default_categories:
        conn.execute('INSERT OR IGNORE INTO categories (name, keywords, color) VALUES (?, ?, ?)', 
                    (cat, keywords, color))
    
    conn.commit()
    conn.close()

def categorize_transaction(description, amount):
    """Auto-categorize transaction based on description keywords"""
    conn = sqlite3.connect('finance.db')
    categories = conn.execute('SELECT name, keywords FROM categories').fetchall()
    conn.close()
    
    description_lower = description.lower()
    
    # TODO: make this smarter, maybe use ML later?
    # Income detection - this is pretty basic but works for now
    if amount > 0:
        if any(word in description_lower for word in ['salary', 'paycheck', 'deposit', 'transfer']):
            return 'Income'
    
    # Expense categorization - just using simple keyword matching
    for cat_name, keywords in categories:
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(',')]
            if any(keyword in description_lower for keyword in keyword_list):
                return cat_name
    
    # Default fallback - could be smarter about this
    return 'Other'

@app.route('/')
def dashboard():
    """Main dashboard with overview stats"""
    conn = sqlite3.connect('finance.db')
    
    # Get recent transactions
    recent = pd.read_sql('''
        SELECT * FROM transactions 
        ORDER BY date DESC, created_at DESC 
        LIMIT 10
    ''', conn)
    
    # Get summary stats
    total_income = conn.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM transactions 
        WHERE amount > 0 AND date >= date('now', '-30 days')
    ''').fetchone()[0]
    
    total_expenses = conn.execute('''
        SELECT COALESCE(SUM(amount), 0) FROM transactions 
        WHERE amount < 0 AND date >= date('now', '-30 days')
    ''').fetchone()[0]
    
    # Category breakdown
    category_data = pd.read_sql('''
        SELECT category, SUM(ABS(amount)) as total
        FROM transactions 
        WHERE amount < 0 AND date >= date('now', '-30 days')
        GROUP BY category
        ORDER BY total DESC
    ''', conn)
    
    conn.close()
    
    return render_template('dashboard.html', 
                         recent_transactions=recent.to_dict('records'),
                         total_income=total_income,
                         total_expenses=abs(total_expenses),
                         net_income=total_income + total_expenses,
                         category_data=category_data.to_dict('records'))

@app.route('/upload')
def upload_page():
    """Upload CSV file page"""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and processing"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.url)
    
    if file and file.filename.lower().endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process the CSV
            df = pd.read_csv(filepath)
            processed_count = process_transactions(df)
            flash(f'Successfully processed {processed_count} transactions', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            return redirect(request.url)
    
    flash('Please upload a CSV file', 'error')
    return redirect(request.url)

def process_transactions(df):
    """Process uploaded CSV and insert transactions"""
    conn = sqlite3.connect('finance.db')
    count = 0
    
    # This part was tricky - different banks use different column names
    # Had to look up a bunch of bank CSV formats online
    possible_date_cols = ['date', 'Date', 'Transaction Date', 'Posted Date']
    possible_desc_cols = ['description', 'Description', 'Memo', 'Transaction']
    possible_amount_cols = ['amount', 'Amount', 'Debit', 'Credit']
    
    date_col = None
    desc_col = None
    amount_col = None
    
    # Find the right columns - this could probably be cleaner
    for col in df.columns:
        if col in possible_date_cols:
            date_col = col
        elif col in possible_desc_cols:
            desc_col = col
        elif col in possible_amount_cols:
            amount_col = col
    
    if not all([date_col, desc_col, amount_col]):
        # Fallback - just guess based on position (not ideal but works)
        cols = list(df.columns)
        date_col = date_col or cols[0]
        desc_col = desc_col or cols[1] 
        amount_col = amount_col or cols[2]
        print(f"Warning: Had to guess columns - using {date_col}, {desc_col}, {amount_col}")  # Debug print
    
    for _, row in df.iterrows():
        try:
            # Parse date
            date_str = str(row[date_col])
            try:
                date_obj = pd.to_datetime(date_str).strftime('%Y-%m-%d')
            except:
                continue
            
            # Parse description
            description = str(row[desc_col]).strip()
            
            # Parse amount - handle negative values and currency symbols
            # Bank CSVs are weird with this stuff
            amount_str = str(row[amount_col]).replace('$', '').replace(',', '').strip()
            if amount_str.startswith('(') and amount_str.endswith(')'):
                # Some banks put negative amounts in parentheses for some reason
                amount_str = '-' + amount_str[1:-1]
            
            try:
                amount = float(amount_str)
            except:
                # Skip rows where amount parsing fails - probably header or bad data
                continue
            
            # Auto-categorize using the function I wrote above
            category = categorize_transaction(description, amount)
            
            # Insert transaction - using parameterized queries for safety
            conn.execute('''
                INSERT INTO transactions (date, description, amount, category, account)
                VALUES (?, ?, ?, ?, ?)
            ''', (date_obj, description, amount, category, 'Uploaded'))
            
            count += 1
            
        except Exception as e:
            # Skip problematic rows but keep going
            print(f"Error processing row: {e}")  # Debug - should probably log this properly
            continue
    
    conn.commit()
    conn.close()
    return count

@app.route('/api/chart-data')
def chart_data():
    """API endpoint for chart data"""
    conn = sqlite3.connect('finance.db')
    
    # Monthly spending trend
    monthly_data = pd.read_sql('''
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as expenses,
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income
        FROM transactions
        WHERE date >= date('now', '-12 months')
        GROUP BY month
        ORDER BY month
    ''', conn)
    
    # Category breakdown (last 30 days)
    category_data = pd.read_sql('''
        SELECT 
            c.name as category,
            c.color,
            SUM(ABS(t.amount)) as amount
        FROM transactions t
        LEFT JOIN categories c ON t.category = c.name
        WHERE t.amount < 0 AND t.date >= date('now', '-30 days')
        GROUP BY t.category, c.color
        ORDER BY amount DESC
    ''', conn)
    
    conn.close()
    
    return jsonify({
        'monthly': monthly_data.to_dict('records'),
        'categories': category_data.to_dict('records')
    })

@app.route('/transactions')
def transactions():
    """View all transactions with filtering"""
    conn = sqlite3.connect('finance.db')
    
    # Get filter parameters
    category_filter = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Build query
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    
    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)
    
    if date_from:
        query += " AND date >= ?"
        params.append(date_from)
    
    if date_to:
        query += " AND date <= ?"
        params.append(date_to)
    
    query += " ORDER BY date DESC, created_at DESC LIMIT 500"
    
    transactions_df = pd.read_sql(query, conn, params=params)
    
    # Get available categories for filter
    categories = conn.execute('SELECT DISTINCT name FROM categories ORDER BY name').fetchall()
    categories = [cat[0] for cat in categories]
    
    conn.close()
    
    return render_template('transactions.html', 
                         transactions=transactions_df.to_dict('records'),
                         categories=categories,
                         filters={
                             'category': category_filter,
                             'date_from': date_from,
                             'date_to': date_to
                         })

if __name__ == '__main__':
    init_db()
    print("Starting Personal Finance Dashboard...")  # Just to see it's running
    app.run(debug=True, port=5001)  # Using 5001 to avoid conflicts with other projects
