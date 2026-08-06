# Library Access Management System

A Flask-based backend application for managing library access, student authorization, and entry/exit tracking.

## Features

- Loads authorized student records from CSV data
- Stores user information and access logs using SQLAlchemy
- Tracks student sign-in and sign-out activity
- Maintains real-time library occupancy counts
- Provides web views for student records and library activity logs

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Pandas
- Jinja2 Templates

## Project Structure

```text
.
├── app.py
├── students_data_sample.csv
├── requirements.txt
└── templates/
    ├── library_view.html
    └── students.html
```

## Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

The application will create the SQLite database automatically and load student records from the CSV file.

## Database Design

The application uses two main models:

- `User` — stores authorized student information
- `LibraryLog` — records sign-in/sign-out events and timestamps

The relationship between users and logs allows each student to have a history of library access activity.
