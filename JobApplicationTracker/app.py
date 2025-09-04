"""
Job Application Tracker
A Flask web app for tracking job applications, interviews, and recruitment progress.

Built this because I was tired of losing track of where I applied and what happened.
Started with a simple spreadsheet but realized I needed something more organized
with better analytics and reminder capabilities.

Features:
- Track applications through the entire process
- Upload resumes and cover letters for each application
- Set reminders for follow-ups and interviews
- Analytics on application success rates
- Export data for reporting
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.secret_key = 'job-tracker-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database setup
def init_db():
    conn = sqlite3.connect('job_tracker.db')
    
    # Applications table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            job_url TEXT,
            date_applied DATE NOT NULL,
            status TEXT DEFAULT 'Applied',
            salary_range TEXT,
            location TEXT,
            recruiter_name TEXT,
            recruiter_email TEXT,
            notes TEXT,
            resume_file TEXT,
            cover_letter_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Status history table - track all status changes
    conn.execute('''
        CREATE TABLE IF NOT EXISTS status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER,
            status TEXT NOT NULL,
            date_changed DATE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    ''')
    
    # Interviews table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER,
            interview_date DATETIME NOT NULL,
            interview_type TEXT,
            interviewer_name TEXT,
            feedback TEXT,
            next_steps TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    ''')
    
    # Reminders table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER,
            reminder_date DATE NOT NULL,
            reminder_type TEXT,
            message TEXT,
            is_completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('job_tracker.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    """Main dashboard with overview stats and charts"""
    conn = get_db_connection()
    
    # Get summary statistics
    total_applications = conn.execute('SELECT COUNT(*) FROM applications').fetchone()[0]
    
    # Status breakdown
    status_counts = conn.execute('''
        SELECT status, COUNT(*) as count 
        FROM applications 
        GROUP BY status
        ORDER BY count DESC
    ''').fetchall()
    
    # Recent applications
    recent_apps = conn.execute('''
        SELECT id, company, position, status, date_applied
        FROM applications 
        ORDER BY date_applied DESC, created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    # Upcoming interviews
    upcoming_interviews = conn.execute('''
        SELECT i.interview_date, i.interview_type, a.company, a.position, i.interviewer_name
        FROM interviews i
        JOIN applications a ON i.application_id = a.id
        WHERE i.interview_date >= date('now')
        ORDER BY i.interview_date ASC
        LIMIT 5
    ''').fetchall()
    
    # Pending reminders
    pending_reminders = conn.execute('''
        SELECT r.reminder_date, r.message, a.company, a.position
        FROM reminders r
        JOIN applications a ON r.application_id = a.id
        WHERE r.is_completed = FALSE AND r.reminder_date <= date('now', '+7 days')
        ORDER BY r.reminder_date ASC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html',
                         total_applications=total_applications,
                         status_counts=status_counts,
                         recent_apps=recent_apps,
                         upcoming_interviews=upcoming_interviews,
                         pending_reminders=pending_reminders)

@app.route('/applications')
def applications():
    """View all applications with filtering and sorting"""
    conn = get_db_connection()
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    company_filter = request.args.get('company', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Build query - this could be cleaner but works for now
    query = "SELECT * FROM applications WHERE 1=1"
    params = []
    
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    
    if company_filter:
        query += " AND company LIKE ?"
        params.append(f'%{company_filter}%')
    
    if date_from:
        query += " AND date_applied >= ?"
        params.append(date_from)
    
    if date_to:
        query += " AND date_applied <= ?"
        params.append(date_to)
    
    query += " ORDER BY date_applied DESC, created_at DESC"
    
    applications = conn.execute(query, params).fetchall()
    
    # Get unique statuses for filter dropdown
    statuses = conn.execute('SELECT DISTINCT status FROM applications ORDER BY status').fetchall()
    
    conn.close()
    
    return render_template('applications.html',
                         applications=applications,
                         statuses=statuses,
                         filters={
                             'status': status_filter,
                             'company': company_filter,
                             'date_from': date_from,
                             'date_to': date_to
                         })

@app.route('/add_application', methods=['GET', 'POST'])
def add_application():
    """Add a new job application"""
    if request.method == 'POST':
        try:
            # Get form data
            company = request.form['company']
            position = request.form['position']
            job_url = request.form.get('job_url', '')
            date_applied = request.form['date_applied']
            status = request.form.get('status', 'Applied')
            salary_range = request.form.get('salary_range', '')
            location = request.form.get('location', '')
            recruiter_name = request.form.get('recruiter_name', '')
            recruiter_email = request.form.get('recruiter_email', '')
            notes = request.form.get('notes', '')
            
            # Handle file uploads
            resume_file = ''
            cover_letter_file = ''
            
            if 'resume' in request.files:
                file = request.files['resume']
                if file and file.filename:
                    filename = secure_filename(f"{company}_{position}_resume_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    resume_file = filename
            
            if 'cover_letter' in request.files:
                file = request.files['cover_letter']
                if file and file.filename:
                    filename = secure_filename(f"{company}_{position}_cover_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    cover_letter_file = filename
            
            # Insert into database
            conn = get_db_connection()
            cursor = conn.execute('''
                INSERT INTO applications 
                (company, position, job_url, date_applied, status, salary_range, location,
                 recruiter_name, recruiter_email, notes, resume_file, cover_letter_file)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company, position, job_url, date_applied, status, salary_range, location,
                  recruiter_name, recruiter_email, notes, resume_file, cover_letter_file))
            
            app_id = cursor.lastrowid
            
            # Add initial status to history
            conn.execute('''
                INSERT INTO status_history (application_id, status, date_changed)
                VALUES (?, ?, ?)
            ''', (app_id, status, date_applied))
            
            conn.commit()
            conn.close()
            
            flash(f'Application to {company} for {position} added successfully!', 'success')
            return redirect(url_for('applications'))
            
        except Exception as e:
            flash(f'Error adding application: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('add_application.html')

@app.route('/application/<int:app_id>')
def application_detail(app_id):
    """View detailed information about a specific application"""
    conn = get_db_connection()
    
    # Get application details
    application = conn.execute('SELECT * FROM applications WHERE id = ?', (app_id,)).fetchone()
    
    if not application:
        flash('Application not found', 'error')
        return redirect(url_for('applications'))
    
    # Get status history
    status_history = conn.execute('''
        SELECT * FROM status_history 
        WHERE application_id = ? 
        ORDER BY date_changed DESC, created_at DESC
    ''', (app_id,)).fetchall()
    
    # Get interviews
    interviews = conn.execute('''
        SELECT * FROM interviews 
        WHERE application_id = ? 
        ORDER BY interview_date DESC
    ''', (app_id,)).fetchall()
    
    # Get reminders
    reminders = conn.execute('''
        SELECT * FROM reminders 
        WHERE application_id = ? 
        ORDER BY reminder_date ASC
    ''', (app_id,)).fetchall()
    
    conn.close()
    
    return render_template('application_detail.html',
                         application=application,
                         status_history=status_history,
                         interviews=interviews,
                         reminders=reminders)

@app.route('/api/dashboard-data')
def dashboard_data():
    """API endpoint for dashboard charts"""
    conn = get_db_connection()
    
    # Applications over time (last 6 months)
    timeline_data = conn.execute('''
        SELECT strftime('%Y-%m', date_applied) as month, COUNT(*) as count
        FROM applications
        WHERE date_applied >= date('now', '-6 months')
        GROUP BY month
        ORDER BY month
    ''').fetchall()
    
    # Status breakdown
    status_data = conn.execute('''
        SELECT status, COUNT(*) as count
        FROM applications
        GROUP BY status
        ORDER BY count DESC
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'timeline': [dict(row) for row in timeline_data],
        'status': [dict(row) for row in status_data]
    })

@app.route('/export')
def export_data():
    """Export all applications to CSV"""
    conn = get_db_connection()
    
    # Get all applications
    df = pd.read_sql_query('''
        SELECT company, position, job_url, date_applied, status, salary_range, location,
               recruiter_name, recruiter_email, notes
        FROM applications
        ORDER BY date_applied DESC
    ''', conn)
    
    conn.close()
    
    # Save to CSV
    filename = f'job_applications_{datetime.now().strftime("%Y%m%d")}.csv'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df.to_csv(filepath, index=False)
    
    return send_file(filepath, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    init_db()
    print("Starting Job Application Tracker...")
    print("Dashboard will be available at http://localhost:5002")
    app.run(debug=True, port=5002)  # Different port to avoid conflicts
