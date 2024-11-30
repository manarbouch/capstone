from datetime import datetime
from flask_login import UserMixin  # Import UserMixin from flask_login
from app import db  # Import db from app.py

class User(UserMixin, db.Model):  # Inherit from UserMixin
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    completed_questionnaire = db.Column(db.Boolean, default=False)

    def get_id(self):
        return str(self.id)  # Flask-Login needs this method

class RiskAssessment(db.Model):
    __tablename__ = 'risk_assessment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal = db.Column(db.String(50), nullable=False)
    time_horizon = db.Column(db.String(50), nullable=False)
    reaction = db.Column(db.String(50), nullable=False)
    savings_rate = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    risk_score = db.Column(db.Integer, nullable=False)
    risk_category = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with User
    user = db.relationship('User', backref=db.backref('risk_assessments', lazy=True))
