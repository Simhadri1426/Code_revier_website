from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    submissions = db.relationship('CodeSubmission', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CodeSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code_text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20))
    detected_language = db.Column(db.String(20))  # Store the detected language
    feedback = db.Column(db.Text)
    ai_score = db.Column(db.Integer)
    comments = db.Column(db.Text)
    plagiarism_hints = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp()) 