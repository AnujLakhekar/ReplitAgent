import subprocess
import tempfile
import os
import logging
import time

def execute_code(code, language='python'):

    supported_languages = {
        'python': {
            'ext': 'py',
            'command': ['python'],
        },
        'javascript': {
            'ext': 'js',
            'command': ['node'],
        },
        'bash': {
            'ext': 'sh',
            'command': ['bash'],
        },
        'ruby': {
            'ext': 'rb',
            'command': ['ruby'],
        }
    }
    
    if language not in supported_languages:
        raise ValueError(f"Unsupported language: {language}. Supported languages are: {', '.join(supported_languages.keys())}")
    
    try:
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(suffix=f'.{supported_languages[language]["ext"]}', delete=False) as temp:
            temp.write(code.encode())
            temp_name = temp.name
        
        # Set execute permissions for the temporary file
        os.chmod(temp_name, 0o755)
        
        # Execute the code and measure execution time
        start_time = time.time()
        result = subprocess.run(
            supported_languages[language]['command'] + [temp_name],
            capture_output=True,
            text=True,
            timeout=10  # Timeout after 10 seconds
        )
        end_time = time.time()
        
        # Remove the temporary file
        os.unlink(temp_name)
        
        # Return the execution results
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'execution_time': end_time - start_time,
            'return_code': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            'stdout': '',
            'stderr': 'Execution timed out after 10 seconds',
            'execution_time': 10,
            'return_code': -1
        }
    except Exception as e:
        logging.error(f"Error executing {language} code: {str(e)}")
        return {
            'stdout': '',
            'stderr': f"Error: {str(e)}",
            'execution_time': 0,
            'return_code': -1
        }

def get_supported_languages():
    """
    Get a list of supported programming languages.
    
    Returns:
        list: List of supported programming languages
    """
    return ['python', 'javascript', 'bash', 'ruby']

def execute_python_with_dependencies(code, dependencies=None):
    """
    Execute Python code after installing dependencies.
    
    Args:
        code (str): The Python code to execute
        dependencies (list): List of dependencies to install before execution
    
    Returns:
        dict: Dictionary containing stdout, stderr, and execution time
    """
    if dependencies is None:
        dependencies = []
    
    try:
        # Create a virtual environment
        venv_dir = tempfile.mkdtemp()
        subprocess.run(['python', '-m', 'venv', venv_dir], check=True)
        
        # Determine the pip executable path based on the platform
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(venv_dir, 'Scripts', 'pip')
        else:  # Unix/Linux/Mac
            pip_path = os.path.join(venv_dir, 'bin', 'pip')
        
        # Install dependencies
        for dependency in dependencies:
            subprocess.run([pip_path, 'install', dependency], check=True)
        
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp:
            temp.write(code.encode())
            temp_name = temp.name
        
        # Determine the python executable path
        if os.name == 'nt':  # Windows
            python_path = os.path.join(venv_dir, 'Scripts', 'python')
        else:  # Unix/Linux/Mac
            python_path = os.path.join(venv_dir, 'bin', 'python')
        
        # Execute the code and measure execution time
        start_time = time.time()
        result = subprocess.run(
            [python_path, temp_name],
            capture_output=True,
            text=True,
            timeout=30  # Longer timeout for code with dependencies
        )
        end_time = time.time()
        
        # Remove the temporary file and virtual environment
        os.unlink(temp_name)
        shutil.rmtree(venv_dir)
        
        # Return the execution results
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'execution_time': end_time - start_time,
            'return_code': result.returncode
        }
        
    except Exception as e:
        logging.error(f"Error executing Python code with dependencies: {str(e)}")
        return {
            'stdout': '',
            'stderr': f"Error: {str(e)}",
            'execution_time': 0,
            'return_code': -1
        }
