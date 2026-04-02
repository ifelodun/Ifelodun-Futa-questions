from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
import json
import random
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


# ======================
# DATABASE MODEL
# ======================
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    grades = db.Column(db.String(500))
    role = db.Column(db.String(20), default='student')


# ======================
# HOME
# ======================
@app.route('/')
def home():
    return redirect(url_for('login'))


# ======================
# LOGIN
# ======================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        student = Student.query.filter_by(email=email).first()

        if student and check_password_hash(student.password, password):
            session['student_id'] = student.id
            session['role'] = student.role

            if student.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))

        flash('Invalid email or password', 'danger')

    return render_template('login.html')


# ======================
# STUDENT DASHBOARD
# ======================
@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session or session.get('role') != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))

    student = Student.query.get(session['student_id'])

    # SAFE JSON LOAD
    grades = {}
    if student and student.grades:
        try:
            grades = json.loads(student.grades)
        except Exception as e:
            print("JSON Error:", e)
            grades = {}

    # SAFE AVERAGE
    average_score = 0
    if grades:
        try:
            average_score = sum(float(v) for v in grades.values()) / len(grades)
        except Exception as e:
            print("Average Error:", e)
            average_score = 0

    return render_template(
        'dashboard.html',
        student=student,
        grades=grades,
        average_score=average_score
    )


# ======================
# RESULT PAGE
# ======================
@app.route('/result')
def result():
    if 'student_id' not in session or session.get('role') != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))

    student = Student.query.get(session['student_id'])

    grades = {}
    if student and student.grades:
        try:
            grades = json.loads(student.grades)
        except Exception as e:
            print("Result JSON Error:", e)
            grades = {}

    return render_template('result.html', student=student, grades=grades)


# ======================
# ADMIN DASHBOARD
# ======================
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'student_id' not in session or session.get('role') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))

    students = Student.query.filter_by(role='student').all()
    return render_template('admin_dashboard.html', students=students)


# ======================
# ADMIN RESET PASSWORD
# ======================
@app.route('/admin_reset/<int:student_id>', methods=['GET', 'POST'])
def admin_reset_student(student_id):
    if 'student_id' not in session or session.get('role') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))

    student = Student.query.get(student_id)

    if request.method == 'POST':
        new_password = request.form['password']
        student.password = generate_password_hash(new_password)
        db.session.commit()
        flash(f"{student.name}'s password has been reset", 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_reset.html', student=student)


# ======================
# FORGOT PASSWORD (OTP)
# ======================
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        student = Student.query.filter_by(email=email).first()

        if student:
            token = serializer.dumps(email, salt='password-reset')
            reset_url = url_for('reset_password', token=token, _external=True)

            otp = random.randint(100000, 999999)
            session['otp'] = otp

            msg = Message(
                'Password Reset OTP',
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = f"Your OTP is: {otp}\nReset link: {reset_url}"

            try:
                mail.send(msg)
                flash('OTP sent to your email', 'info')
            except Exception as e:
                print("Mail Error:", e)
                flash('Error sending email', 'danger')

            return redirect(url_for('reset_password', token=token))

        flash('Email not found', 'danger')

    return render_template('forgot_password.html')


# ======================
# RESET PASSWORD
# ======================
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except:
        flash('Reset link invalid or expired', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        otp_input = request.form['otp']
        password = request.form['password']

        if str(otp_input) == str(session.get('otp')):
            student = Student.query.filter_by(email=email).first()
            student.password = generate_password_hash(password)
            db.session.commit()
            flash('Password reset successful', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP', 'danger')

    return render_template('reset_password.html')


# ======================
# LOGOUT
# ======================
@app.route('/logout')
def logout():
    session.pop('student_id', None)
    session.pop('role', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))


# ======================
# RUN APP
# ======================
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
