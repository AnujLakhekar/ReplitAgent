import os
import shutil
import json
import logging
import datetime
from utils import file_operations

def create_project(name, template=None):
    """
    Create a new project with the given name and optional template.
    
    Args:
        name (str): Name of the project
        template (str, optional): Template to use for the project. Defaults to None.
    
    Returns:
        bool: True if the project was created successfully
    """
    try:
        # Create the project directory
        if not os.path.exists(name):
            os.makedirs(name)
        else:
            raise FileExistsError(f"Project '{name}' already exists")
        
        # Initialize with template if provided
        if template:
            initialize_from_template(name, template)
        else:
            # Create basic project structure
            create_basic_structure(name)
        
        # Create project metadata
        create_project_metadata(name)
        
        logging.info(f"Created project '{name}'")
        return True
    except Exception as e:
        logging.error(f"Error creating project '{name}': {str(e)}")
        raise

def initialize_from_template(project_name, template):
    """
    Initialize a project from a template.
    
    Args:
        project_name (str): Name of the project
        template (str): Template to use
    """
    templates = {
        'python': {
            'files': {
                'main.py': '# Main entry point for the application\n\ndef main():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    main()',
                'requirements.txt': '# List your dependencies here\n',
                'README.md': f'# {project_name}\n\nA Python project created with Replit Agent.\n'
            },
            'directories': ['src', 'tests']
        },
        'web': {
            'files': {
                'index.html': f'<!DOCTYPE html>\n<html>\n<head>\n    <title>{project_name}</title>\n    <link rel="stylesheet" href="styles.css">\n</head>\n<body>\n    <h1>{project_name}</h1>\n    <p>A web project created with Replit Agent.</p>\n    <script src="script.js"></script>\n</body>\n</html>',
                'styles.css': '/* Your styles here */\nbody {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n}',
                'script.js': '// Your JavaScript code here\nconsole.log("Hello, World!");',
                'README.md': f'# {project_name}\n\nA web project created with Replit Agent.\n'
            },
            'directories': ['assets', 'js', 'css']
        },
        'flask': {
            'files': {
                'app.py': 'from flask import Flask, render_template\n\napp = Flask(__name__)\n\n@app.route("/")\ndef home():\n    return render_template("index.html")\n\nif __name__ == "__main__":\n    app.run(host="0.0.0.0", port=5000, debug=True)',
                'requirements.txt': 'flask==2.0.1\n',
                'README.md': f'# {project_name}\n\nA Flask project created with Replit Agent.\n'
            },
            'directories': ['static', 'templates', 'routes']
        }
    }
    
    if template not in templates:
        raise ValueError(f"Unknown template: {template}. Available templates: {', '.join(templates.keys())}")
    
    # Create the base directory structure
    for directory in templates[template]['directories']:
        os.makedirs(os.path.join(project_name, directory), exist_ok=True)
    
    # Create template files
    for file_path, content in templates[template]['files'].items():
        file_operations.write_file(os.path.join(project_name, file_path), content)
    
    # Create extra directories for specific templates
    if template == 'flask':
        # Create the templates directory with a basic index.html
        index_html = f'<!DOCTYPE html>\n<html>\n<head>\n    <title>{project_name}</title>\n    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'styles.css\') }}">\n</head>\n<body>\n    <h1>{project_name}</h1>\n    <p>A Flask project created with Replit Agent.</p>\n</body>\n</html>'
        file_operations.write_file(os.path.join(project_name, 'templates', 'index.html'), index_html)
        
        # Create a basic CSS file
        css_content = '/* Your styles here */\nbody {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n}'
        file_operations.write_file(os.path.join(project_name, 'static', 'styles.css'), css_content)

def create_basic_structure(project_name):
    """
    Create a basic project structure.
    
    Args:
        project_name (str): Name of the project
    """
    # Create basic directories
    os.makedirs(os.path.join(project_name, 'src'), exist_ok=True)
    os.makedirs(os.path.join(project_name, 'docs'), exist_ok=True)
    
    # Create basic files
    readme_content = f"# {project_name}\n\nA project created with Replit Agent.\n"
    file_operations.write_file(os.path.join(project_name, 'README.md'), readme_content)
    
    gitignore_content = "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nbuild/\ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/\nparts/\nsdist/\nvar/\nwheels/\n*.egg-info/\n.installed.cfg\n*.egg\n\n# Environment\n.env\n.venv\nenv/\nvenv/\nENV/\nenv.bak/\nvenv.bak/\n\n# IDE\n.idea/\n.vscode/\n*.swp\n*.swo\n"
    file_operations.write_file(os.path.join(project_name, '.gitignore'), gitignore_content)

def create_project_metadata(project_name):
    """
    Create project metadata file.
    
    Args:
        project_name (str): Name of the project
    """
    metadata = {
        'name': project_name,
        'created_at': datetime.datetime.now().isoformat(),
        'created_by': 'Replit Agent',
        'description': f'A project named {project_name}',
        'version': '0.1.0'
    }
    
    file_operations.write_file(
        os.path.join(project_name, '.project_metadata.json'),
        json.dumps(metadata, indent=4)
    )

def list_projects(directory='.'):
    """
    List all projects in the specified directory.
    
    Args:
        directory (str): Directory to search for projects
    
    Returns:
        list: List of project names
    """
    try:
        projects = []
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            if os.path.isdir(path) and os.path.exists(os.path.join(path, '.project_metadata.json')):
                projects.append(item)
        return projects
    except Exception as e:
        logging.error(f"Error listing projects in directory {directory}: {str(e)}")
        raise

def get_project_info(project_name):
    """
    Get information about a project.
    
    Args:
        project_name (str): Name of the project
    
    Returns:
        dict: Project metadata
    """
    try:
        metadata_path = os.path.join(project_name, '.project_metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"Project metadata not found for '{project_name}'")
    except Exception as e:
        logging.error(f"Error getting project info for '{project_name}': {str(e)}")
        raise

def delete_project(project_name):
    """
    Delete a project.
    
    Args:
        project_name (str): Name of the project
    
    Returns:
        bool: True if the project was deleted successfully
    """
    try:
        if os.path.exists(project_name) and os.path.isdir(project_name):
            shutil.rmtree(project_name)
            logging.info(f"Deleted project '{project_name}'")
            return True
        else:
            raise FileNotFoundError(f"Project '{project_name}' not found")
    except Exception as e:
        logging.error(f"Error deleting project '{project_name}': {str(e)}")
        raise

def update_project_metadata(project_name, metadata):
    """
    Update project metadata.
    
    Args:
        project_name (str): Name of the project
        metadata (dict): New metadata to merge with existing
    
    Returns:
        dict: Updated metadata
    """
    try:
        metadata_path = os.path.join(project_name, '.project_metadata.json')
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                current_metadata = json.load(f)
        else:
            current_metadata = {}
        
        # Merge the new metadata with the existing metadata
        current_metadata.update(metadata)
        current_metadata['updated_at'] = datetime.datetime.now().isoformat()
        
        file_operations.write_file(
            metadata_path,
            json.dumps(current_metadata, indent=4)
        )
        
        return current_metadata
    except Exception as e:
        logging.error(f"Error updating metadata for project '{project_name}': {str(e)}")
        raise
