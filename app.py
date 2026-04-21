from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)

# ====================== النماذج (Models) ======================
class Trail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.String(50))
    distance = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    description = db.Column(db.Text)
    image = db.Column(db.String(300))  # رابط الصورة

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100))
    bio = db.Column(db.Text)
    photo = db.Column(db.String(300))

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    trail_id = db.Column(db.Integer, db.ForeignKey('trail.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registration.id'))
    rating = db.Column(db.Integer)  # 1-5
    comment = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()

# ====================== الصفحات ======================
@app.route('/')
def index():
    trails = Trail.query.all()
    return render_template('index.html', trails=trails)

@app.route('/trails')
def trails():
    trails = Trail.query.all()
    return render_template('trails.html', trails=trails)

@app.route('/trail/<int:id>')
def trail_detail(id):
    trail = Trail.query.get_or_404(id)
    return render_template('trail_detail.html', trail=trail)

@app.route('/team')
def team():
    members = TeamMember.query.all()
    return render_template('team.html', members=members)

@app.route('/register/<int:trail_id>', methods=['GET', 'POST'])
def register(trail_id):
    if request.method == 'POST':
        reg = Registration(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form.get('phone'),
            trail_id=trail_id
        )
        db.session.add(reg)
        db.session.commit()
        flash('تم التسجيل بنجاح! شكرًا لك.', 'success')
        return redirect(url_for('feedback', reg_id=reg.id))
    trail = Trail.query.get_or_404(trail_id)
    return render_template('register.html', trail=trail)

@app.route('/feedback/<int:reg_id>', methods=['GET', 'POST'])
def feedback(reg_id):
    if request.method == 'POST':
        fb = Feedback(
            registration_id=reg_id,
            rating=int(request.form['rating']),
            comment=request.form['comment']
        )
        db.session.add(fb)
        db.session.commit()
        flash('شكرًا على رأيك!', 'success')
        return redirect(url_for('index'))
    return render_template('feedback.html')

# ====================== لوحة الإدارة (بسيطة) ======================
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form['password'] != 'admin123':  # غيّرها لاحقًا
            flash('كلمة مرور خاطئة', 'danger')
            return redirect(url_for('admin'))
        
        # إضافة مسار جديد (مثال)
        if 'add_trail' in request.form:
            trail = Trail(
                name=request.form['name'],
                location=request.form['location'],
                difficulty=request.form['difficulty'],
                distance=request.form['distance'],
                duration=request.form['duration'],
                description=request.form['description'],
                image=request.form.get('image')
            )
            db.session.add(trail)
            db.session.commit()
            flash('تم إضافة المسار', 'success')
    trails = Trail.query.all()
    registrations = Registration.query.all()
    return render_template('admin/dashboard.html', trails=trails, registrations=registrations)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
