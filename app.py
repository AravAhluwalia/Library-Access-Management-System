from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime

# Initialize Flask application
app = Flask(__name__)

# Configure SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students_library.db'

# Initialize SQLAlchemy object
db = SQLAlchemy(app)


# Define User and LibraryLog models
class User(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class LibraryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
    time_in = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    time_out = db.Column(db.DateTime)

    # Define relationship with User model
    user = db.relationship('User', backref=db.backref('library_logs', lazy=True))


# Create tables in database
with app.app_context():
    db.create_all()


# Function to load student data from CSV file into database
def load_student_data():
    try:
        print("Attempting to load data from CSV file.")

        # Load CSV from project directory
        data = pd.read_csv('students_data.csv', delimiter=',')

        # Check if dataframe is empty
        if data.empty:
            print("Error: CSV file is empty.")
            return

        if not data.columns.any():
            print("Error: CSV file does not have columns.")
            return

        print("Loaded Data:")

        # Iterate over each student
        for _, row in data.iterrows():

            if 'id_code' in row:
                name = row['name']
                id_code = str(row['id_code'])

                # Check if user already exists
                user_exists = User.query.filter_by(id=id_code).first()

                if not user_exists:
                    new_user = User(
                        id=id_code,
                        name=name
                    )
                    db.session.add(new_user)

            else:
                print(f"Warning: 'id_code' not found in row #{row}.")

        # Commit all inserted users once
        db.session.commit()

        print("Data loaded successfully.")

    except Exception as e:
        print(
            f"Error during data loading. "
            f"Exception Type: {type(e).__name__}, Message: {e}"
        )


# Endpoint for viewing authorized students
@app.route('/students')
def students():
    students = User.query.all()
    return render_template('students.html', students=students)


# Endpoint for user sign-in
@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    user_id = data.get('user_id')

    user = User.query.get(user_id)

    if user:
        log_entry = LibraryLog(user_id=user_id)
        db.session.add(log_entry)
        db.session.commit()

        return jsonify(
            message=f"{user.name} signed in successfully."
        ), 201

    else:
        return jsonify(error="User not found."), 404


# Endpoint for user sign-out
@app.route('/signout', methods=['POST'])
def signout():
    data = request.json
    user_id = data.get('user_id')

    user = User.query.get(user_id)

    if user:
        log_entry = LibraryLog.query.filter_by(
            user_id=user_id,
            time_out=None
        ).first()

        if log_entry:
            log_entry.time_out = datetime.utcnow()
            db.session.commit()

            return jsonify(
                message=f"{user.name} signed out successfully."
            ), 200

        else:
            return jsonify(
                error="User is not currently signed in."
            ), 400

    else:
        return jsonify(error="User not found."), 404


# Endpoint for combined sign-in/sign-out action
@app.route('/library_action', methods=['POST'])
def library_action():
    data = request.form
    user_id = data.get('user_id')

    user = User.query.get(user_id)

    if user:

        # Check if currently signed in
        log_entry = LibraryLog.query.filter_by(
            user_id=user_id,
            time_out=None
        ).first()

        if log_entry:
            # Sign out
            log_entry.time_out = datetime.utcnow()
            db.session.commit()

            message = f"{user.name} signed out successfully."

        else:
            # Sign in
            log_entry = LibraryLog(user_id=user_id)
            db.session.add(log_entry)
            db.session.commit()

            message = f"{user.name} signed in successfully."


        # Count currently signed-in students
        signed_in_count = LibraryLog.query.filter(
            LibraryLog.time_out.is_(None)
        ).count()

        library_logs = LibraryLog.query.all()

        return render_template(
            'library_view.html',
            library_logs=library_logs,
            message=message,
            signed_in_count=signed_in_count
        )

    else:
        return jsonify(error="User not found."), 404


# Endpoint for viewing library database
@app.route('/library_view')
def library_view():

    library_logs = LibraryLog.query.all()

    signed_in_count = LibraryLog.query.filter(
        LibraryLog.time_out.is_(None)
    ).count()

    return render_template(
        'library_view.html',
        library_logs=library_logs,
        signed_in_count=signed_in_count
    )


if __name__ == '__main__':

    with app.app_context():
        load_student_data()

    app.run(debug=True)