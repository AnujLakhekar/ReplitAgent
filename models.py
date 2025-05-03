from app import db
from datetime import datetime

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FileOperation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(20), nullable=False)  # create, read, update, delete
    file_path = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
class CodeExecution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(50), nullable=False)
    code_snippet = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text)
    execution_time = db.Column(db.Float)  # in seconds
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class GitOperation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(50), nullable=False)  # commit, push, pull, etc.
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PackageOperation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(20), nullable=False)  # install, uninstall, update
    package_name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AIInteraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
