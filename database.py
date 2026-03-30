from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

# Association tables for many-to-many relationships
project_skills = db.Table(
    'project_skills',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)

experience_skills = db.Table(
    'experience_skills',
    db.Column('experience_id', db.Integer, db.ForeignKey('experience.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """Admin user for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SkillCategory(db.Model):
    """Categories for grouping skills"""
    __tablename__ = 'skill_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), default='fa-star')
    order = db.Column(db.Integer, default=0)
    skills = db.relationship('Skill', backref='category', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Skill(db.Model):
    """Individual skills"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('skill_category.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Skill {self.name}>'


class Project(db.Model):
    """Portfolio projects"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Hardware, Web, 3D Model, etc.
    image_filename = db.Column(db.String(255), nullable=True)
    details = db.Column(db.Text, nullable=True)  # Additional project details
    skills = db.relationship('Skill', secondary=project_skills, lazy='subquery',
                            backref=db.backref('projects', lazy=True))
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Project {self.title}>'


class Experience(db.Model):
    """Work experience entries"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    period = db.Column(db.String(100), nullable=False)  # e.g., "Jan 2023 - Present"
    description = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text, nullable=False)  # JSON string of responsibilities
    skills = db.relationship('Skill', secondary=experience_skills, lazy='subquery',
                            backref=db.backref('experiences', lazy=True))
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_responsibilities(self):
        """Parse responsibilities JSON"""
        try:
            return json.loads(self.responsibilities)
        except:
            return []

    def set_responsibilities(self, resp_list):
        """Store responsibilities as JSON"""
        self.responsibilities = json.dumps(resp_list)

    def __repr__(self):
        return f'<Experience {self.title} at {self.company}>'


class Education(db.Model):
    """Education history"""
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(100), nullable=False)  # BS, Intermediate, Matriculation
    field = db.Column(db.String(200), nullable=False)
    school = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    period = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(50), nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON with subjects, credits, etc.
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_details(self):
        """Parse details JSON"""
        try:
            return json.loads(self.details) if self.details else {}
        except:
            return {}

    def set_details(self, details_dict):
        """Store details as JSON"""
        self.details = json.dumps(details_dict) if details_dict else None

    def __repr__(self):
        return f'<Education {self.level} in {self.field}>'


class ContactMessage(db.Model):
    """Messages submitted via the contact form"""
    __tablename__ = 'contact_message'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(300), nullable=False)
    message = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(50), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # AI Integration Fields
    ai_category = db.Column(db.String(50), nullable=True)
    ai_draft = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<ContactMessage from {self.name} ({self.email})>'

class Visitor(db.Model):
    """Tracking daily visitors by their IP address"""
    __tablename__ = 'visitor'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(300), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Visitor {self.ip_address}>'
