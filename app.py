import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure the database if available
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    db.init_app(app)

    with app.app_context():
        # Import models here
        import models
        db.create_all()
else:
    logging.warning("No DATABASE_URL found in environment variables. Database functionality disabled.")
# Import utility modules

from utils import file_operations, code_execution, project_management, \
                 git_integration, package_management, user_interaction, \
                 ai_features, api_utils, db_helper

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/file-operations')
def file_ops():
    return render_template('file_operations.html')

@app.route('/api/file/list', methods=['GET'])
def list_files():
    path = request.args.get('path', '.')
    try:
        files = file_operations.list_files(path)
        return jsonify({"status": "success", "files": files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/file/read', methods=['GET'])
def read_file():
    path = request.args.get('path')
    if not path:
        return jsonify({"status": "error", "message": "No file path provided"}), 400
    try:
        content = file_operations.read_file(path)
        return jsonify({"status": "success", "content": content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/file/write', methods=['POST'])
def write_file():
    data = request.json
    path = data.get('path')
    content = data.get('content')
    if not path or content is None:
        return jsonify({"status": "error", "message": "Missing path or content"}), 400
    try:
        file_operations.write_file(path, content)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/file/delete', methods=['POST'])
def delete_file():
    data = request.json
    path = data.get('path')
    if not path:
        return jsonify({"status": "error", "message": "No file path provided"}), 400
    try:
        file_operations.delete_file(path)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/code-execution')
def code_exec():
    return render_template('code_execution.html')

@app.route('/api/code/execute', methods=['POST'])
def execute_code():
    data = request.json
    code = data.get('code')
    language = data.get('language', 'python')
    if not code:
        return jsonify({"status": "error", "message": "No code provided"}), 400
    try:
        result = code_execution.execute_code(code, language)
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/project-management')
def project_mgmt():
    return render_template('project_management.html')

@app.route('/api/project/create', methods=['POST'])
def create_project():
    data = request.json
    name = data.get('name')
    template = data.get('template')
    if not name:
        return jsonify({"status": "error", "message": "No project name provided"}), 400
    try:
        project_management.create_project(name, template)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/git-integration')
def git_page():
    return render_template('git_integration.html')

@app.route('/api/git/status', methods=['GET'])
def git_status():
    try:
        status = git_integration.get_status()
        return jsonify({"status": "success", "git_status": status})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/git/commit', methods=['POST'])
def git_commit():
    data = request.json
    message = data.get('message')
    if not message:
        return jsonify({"status": "error", "message": "No commit message provided"}), 400
    try:
        git_integration.commit(message)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/package-management')
def package_mgmt():
    return render_template('package_management.html')

@app.route('/api/package/install', methods=['POST'])
def install_package():
    data = request.json
    package_name = data.get('package')
    if not package_name:
        return jsonify({"status": "error", "message": "No package name provided"}), 400
    try:
        package_management.install_package(package_name)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/ai-features')
def ai_page():
    return render_template('ai_features.html')

@app.route('/api/ai/generate', methods=['POST'])
def generate_code():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"status": "error", "message": "No prompt provided"}), 400
    try:
        generated_code = ai_features.generate_code(prompt)
        return jsonify({"status": "success", "generated_code": generated_code})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api-utils')
def api_page():
    return render_template('api_utils.html')

@app.route('/api/external/fetch', methods=['POST'])
def fetch_external():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400
    try:
        response = api_utils.fetch_data(url)
        return jsonify({"status": "success", "data": response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/database')
def database_page():
    return render_template('database.html')

@app.route('/api/db/collections', methods=['GET'])
def get_collections():
    try:
        collections = db_helper.get_collections()
        return jsonify({"status": "success", "collections": collections})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/db/documents', methods=['GET'])
def get_documents():
    collection_name = request.args.get('collection')
    if not collection_name:
        return jsonify({"status": "error", "message": "No collection name provided"}), 400
    try:
        documents = db_helper.list_documents(collection_name)
        return jsonify({"status": "success", "documents": documents})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/db/document', methods=['POST'])
def create_document():
    data = request.json
    collection_name = data.get('collection')
    document_data = data.get('data')
    if not collection_name or not document_data:
        return jsonify({"status": "error", "message": "Missing collection name or document data"}), 400
    try:
        document_id = db_helper.create_document(collection_name, document_data)
        return jsonify({"status": "success", "document_id": document_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
