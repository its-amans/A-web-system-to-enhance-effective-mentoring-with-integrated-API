from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import pymysql

# Install pymysql as MySQLdb
pymysql.install_as_MySQLdb()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure SQLAlchemy and file upload folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://aman:Aman8601@localhost/login_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize database
db = SQLAlchemy(app)

# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    occupation = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('mentor', 'mentee'), nullable=False)
    certificate_path = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)

# Routes
@app.route('/', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        # Retrieve form data
        fullname = request.form.get('fullname')
        password = request.form.get('password')

        # Validate credentials
        user = User.query.filter_by(fullname=fullname).first()
        if user and check_password_hash(user.password_hash, password):
            # Store user session (using their ID)
            session['user_id'] = user.id
            return redirect('/index.html')  # Redirect to the index page after successful login
        else:
            flash('Invalid credentials. Please try again.')
            return redirect('/')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        fullname = request.form.get('fullname')
        occupation = request.form.get('occupation')
        role = request.form.get('role')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate passwords
        if not password or not confirm_password:
            flash('Password fields cannot be empty!')
            return redirect('/register')
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect('/register')

        # Hash the password
        password_hash = generate_password_hash(password)

        # Handle certificate upload for mentors
        certificate_path = None
        if role == 'mentor':
            file = request.files.get('certificate')
            if not file or file.filename.strip() == '':
                flash('Certificate is required for mentors.')
                return redirect('/register')
            certificate_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(certificate_path)

        # Check if user already exists
        existing_user = User.query.filter_by(fullname=fullname, role=role).first()
        if existing_user:
            flash('User already exists. Please sign in.')
            return redirect('/')

        # Save new user to database
        new_user = User(
            fullname=fullname,
            occupation=occupation,
            role=role,
            certificate_path=certificate_path,
            password_hash=password_hash
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please sign in to continue.')
        return redirect('/')

    return render_template('register.html')

@app.route('/index.html')
def index():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect('/')  # If not logged in, redirect to login page
    
    return render_template('index.html')

if __name__ == '__main__':
    # Create the upload folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
