from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
import random, json

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# =====================
# Database Model
# =====================
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    grades = db.Column(db.String(500))  # JSON string for scores
    role = db.Column(db.String(20), default='student')  # 'student' or 'admin'

# =====================
# Routes
# =====================

@app.route('/')
def home():
    return redirect(url_for('login'))

# --------------------- Login ---------------------
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
            else:
                return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

# --------------------- Dashboard (Student) ---------------------
@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session or session.get('role') != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    grades = json.loads(student.grades) if student.grades else {}
    average_score = sum(grades.values()) / len(grades) if grades else 0
    return render_template('dashboard.html', student=student, average_score=average_score)

# --------------------- Admin Dashboard ---------------------
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'student_id' not in session or session.get('role') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    students = Student.query.filter_by(role='student').all()
    return render_template('admin_dashboard.html', students=students)

# --------------------- Admin Reset Student ---------------------
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

# --------------------- Forgot Password ---------------------
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
            msg = Message('Password Reset OTP', sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f"Your OTP for password reset is: {otp}\nReset link: {reset_url}"
            mail.send(msg)
            flash('OTP sent to your email', 'info')
            return redirect(url_for('reset_password', token=token))
        flash('Email not found', 'danger')
    return render_template('forgot_password.html')

# --------------------- Reset Password ---------------------
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except:
        flash('The reset link is invalid or expired', 'danger')
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

# --------------------- Result Slip ---------------------
@app.route('/result')
def result():
    if 'student_id' not in session or session.get('role') != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    grades = json.loads(student.grades) if student.grades else {}
    return render_template('result.html', student=student, grades=grades)

# --------------------- Logout ---------------------
@app.route('/logout')
def logout():
    session.pop('student_id', None)
    session.pop('role', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

# =====================
# Run App
# =====================
if __name__ == '__main__':
    db.create_all()
    # Create default admin if not exists
    if not Student.query.filter_by(email='noplysola@gmail.com').first():
        admin = Student(
            name='Ifelodun',
            email='noplysola@gmail.com',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
    app.run(debug=True)
