import subprocess
import logging
import os
import json

def install_package(package_name, language='python'):
    """
    Install a package using the appropriate package manager.
    
    Args:
        package_name (str): Name of the package to install
        language (str): Language of the package manager to use
    
    Returns:
        bool: True if installation was successful
    """
    package_managers = {
        'python': ['pip', 'install'],
        'javascript': ['npm', 'install'],
        'ruby': ['gem', 'install']
    }
    
    if language not in package_managers:
        raise ValueError(f"Unsupported language: {language}. Supported languages are: {', '.join(package_managers.keys())}")
    
    try:
        # Add a version specifier if provided
        if '>=' in package_name or '==' in package_name or '<=' in package_name:
            packages = [package_name]
        else:
            packages = [package_name]
        
        cmd = package_managers[language] + packages
        logging.info(f"Installing package: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logging.info(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install package {package_name}: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error installing package {package_name}: {str(e)}")
        raise

def uninstall_package(package_name, language='python'):
    """
    Uninstall a package using the appropriate package manager.
    
    Args:
        package_name (str): Name of the package to uninstall
        language (str): Language of the package manager to use
    
    Returns:
        bool: True if uninstallation was successful
    """
    package_managers = {
        'python': ['pip', 'uninstall', '-y'],
        'javascript': ['npm', 'uninstall'],
        'ruby': ['gem', 'uninstall', '-x']
    }
    
    if language not in package_managers:
        raise ValueError(f"Unsupported language: {language}. Supported languages are: {', '.join(package_managers.keys())}")
    
    try:
        cmd = package_managers[language] + [package_name]
        logging.info(f"Uninstalling package: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logging.info(f"Successfully uninstalled {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to uninstall package {package_name}: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error uninstalling package {package_name}: {str(e)}")
        raise

def list_installed_packages(language='python'):
    """
    List all installed packages using the appropriate package manager.
    
    Args:
        language (str): Language of the package manager to use
    
    Returns:
        list: List of installed packages
    """
    package_managers = {
        'python': ['pip', 'list', '--format=json'],
        'javascript': ['npm', 'list', '--json'],
        'ruby': ['gem', 'list', '-e']
    }
    
    if language not in package_managers:
        raise ValueError(f"Unsupported language: {language}. Supported languages are: {', '.join(package_managers.keys())}")
    
    try:
        cmd = package_managers[language]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        if language == 'python':
            packages = json.loads(result.stdout)
            return [{'name': pkg['name'], 'version': pkg['version']} for pkg in packages]
        elif language == 'javascript':
            data = json.loads(result.stdout)
            dependencies = data.get('dependencies', {})
            return [{'name': name, 'version': info.get('version', '')} for name, info in dependencies.items()]
        elif language == 'ruby':
            # Parse the output of gem list
            packages = []
            for line in result.stdout.splitlines():
                if line.strip():
                    parts = line.split(' ')
                    name = parts[0]
                    version = parts[1].strip('()')
                    packages.append({'name': name, 'version': version})
            return packages
        
        return []
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to list installed packages: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error listing installed packages: {str(e)}")
        raise

def check_package_installed(package_name, language='python'):
    """
    Check if a package is installed.
    
    Args:
        package_name (str): Name of the package to check
        language (str): Language of the package manager to use
    
    Returns:
        bool: True if the package is installed
    """
    try:
        packages = list_installed_packages(language)
        return any(pkg['name'].lower() == package_name.lower() for pkg in packages)
    except Exception as e:
        logging.error(f"Error checking if package {package_name} is installed: {str(e)}")
        raise

def get_package_version(package_name, language='python'):
    """
    Get the version of an installed package.
    
    Args:
        package_name (str): Name of the package to check
        language (str): Language of the package manager to use
    
    Returns:
        str: Version of the package, or None if not installed
    """
    try:
        packages = list_installed_packages(language)
        for pkg in packages:
            if pkg['name'].lower() == package_name.lower():
                return pkg['version']
        return None
    except Exception as e:
        logging.error(f"Error getting version of package {package_name}: {str(e)}")
        raise

def create_requirements_file(output_file='requirements.txt', language='python'):
    """
    Create a requirements file for the current environment.
    
    Args:
        output_file (str): Name of the output file
        language (str): Language of the package manager to use
    
    Returns:
        bool: True if the file was created successfully
    """
    try:
        if language == 'python':
            result = subprocess.run(
                ['pip', 'freeze'],
                capture_output=True,
                text=True,
                check=True
            )
            with open(output_file, 'w') as f:
                f.write(result.stdout)
            return True
        elif language == 'javascript':
            # Check if package.json exists
            if os.path.exists('package.json'):
                return True
            else:
                # Create a basic package.json file
                package_json = {
                    "name": os.path.basename(os.getcwd()),
                    "version": "1.0.0",
                    "description": "Created by Replit Agent",
                    "main": "index.js",
                    "dependencies": {}
                }
                with open('package.json', 'w') as f:
                    json.dump(package_json, f, indent=2)
                return True
        else:
            raise ValueError(f"Requirements file generation not supported for language: {language}")
    except Exception as e:
        logging.error(f"Error creating requirements file: {str(e)}")
        raise
