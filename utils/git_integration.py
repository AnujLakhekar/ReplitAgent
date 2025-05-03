import os
import subprocess
import logging
import base64
from urllib.parse import urlparse

def init_repo(directory='.'):
    """
    Initialize a Git repository in the specified directory.
    
    Args:
        directory (str): Directory to initialize the repository in
    
    Returns:
        bool: True if initialization was successful
    """
    try:
        result = subprocess.run(
            ['git', 'init'],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True
        )
        logging.info(f"Initialized Git repository in {directory}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to initialize Git repository: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error initializing Git repository: {str(e)}")
        raise

def clone_repo(url, directory='.'):
    """
    Clone a Git repository from the specified URL.
    
    Args:
        url (str): URL of the repository to clone
        directory (str): Directory to clone the repository into
    
    Returns:
        bool: True if cloning was successful
    """
    try:
        # Parse the URL to check if it contains credentials
        parsed_url = urlparse(url)
        if parsed_url.username or parsed_url.password:
            # Reconstruct the URL without credentials for logging
            sanitized_url = f"{parsed_url.scheme}://{parsed_url.netloc.split('@')[-1]}{parsed_url.path}"
            logging.info(f"Cloning repository from {sanitized_url}")
        else:
            logging.info(f"Cloning repository from {url}")
        
        result = subprocess.run(
            ['git', 'clone', url, directory],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to clone repository: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error cloning repository: {str(e)}")
        raise

def add_files(paths, directory='.'):
    """
    Add files to the Git staging area.
    
    Args:
        paths (list): List of file paths to add
        directory (str): Repository directory
    
    Returns:
        bool: True if adding was successful
    """
    try:
        # Convert single path to list
        if isinstance(paths, str):
            paths = [paths]
        
        result = subprocess.run(
            ['git', 'add'] + paths,
            cwd=directory,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to add files to Git: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error adding files to Git: {str(e)}")
        raise

def commit(message, directory='.'):
    """
    Commit changes to the Git repository.
    
    Args:
        message (str): Commit message
        directory (str): Repository directory
    
    Returns:
        bool: True if commit was successful
    """
    try:
        # Configure Git user if not already configured
        ensure_git_config(directory)
        
        result = subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        # Check if the error is due to nothing to commit
        if "nothing to commit" in e.stderr:
            logging.info("Nothing to commit, working tree clean")
            return False
        logging.error(f"Failed to commit to Git: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error committing to Git: {str(e)}")
        raise

def push(remote='origin', branch='main', directory='.'):
    """
    Push changes to a remote repository.
    
    Args:
        remote (str): Name of the remote
        branch (str): Name of the branch
        directory (str): Repository directory
    
    Returns:
        bool: True if push was successful
    """
    try:
        result = subprocess.run(
            ['git', 'push', remote, branch],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to push to Git: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error pushing to Git: {str(e)}")
        raise

def pull(remote='origin', branch='main', directory='.'):
    """
    Pull changes from a remote repository.
    
    Args:
        remote (str): Name of the remote
        branch (str): Name of the branch
        directory (str): Repository directory
    
    Returns:
        bool: True if pull was successful
    """
    try:
        result = subprocess.run(
            ['git', 'pull', remote, branch],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to pull from Git: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error pulling from Git: {str(e)}")
        raise

def get_status(directory='.'):
    """
    Get the status of the Git repository.
    
    Args:
        directory (str): Repository directory
    
    Returns:
        str: Status message
    """
    try:
        result = subprocess.run(
            ['git', 'status'],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to get Git status: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error getting Git status: {str(e)}")
        raise

def get_log(limit=10, directory='.'):
    """
    Get the commit log of the Git repository.
    
    Args:
        limit (int): Maximum number of commits to return
        directory (str): Repository directory
    
    Returns:
        str: Commit log
    """
    try:
        result = subprocess.run(
            ['git', 'log', f'-{limit}', '--oneline'],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to get Git log: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error getting Git log: {str(e)}")
        raise

def create_branch(branch_name, directory='.'):
    """
    Create a new Git branch.
    
    Args:
        branch_name (str): Name of the branch to create
        directory (str): Repository directory
    
    Returns:
        bool: True if branch creation was successful
    """
    try:
        result = subprocess.run(
            ['git', 'branch', branch_name],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to create Git branch: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error creating Git branch: {str(e)}")
        raise

def checkout_branch(branch_name, directory='.'):
    """
    Checkout a Git branch.
    
    Args:
        branch_name (str): Name of the branch to checkout
        directory (str): Repository directory
    
    Returns:
        bool: True if checkout was successful
    """
    try:
        result = subprocess.run(
            ['git', 'checkout', branch_name],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to checkout Git branch: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Error checking out Git branch: {str(e)}")
        raise

def ensure_git_config(directory='.'):
    """
    Ensure that Git user name and email are configured.
    If not, set default values.
    
    Args:
        directory (str): Repository directory
    """
    try:
        # Check if user name is configured
        name_result = subprocess.run(
            ['git', 'config', 'user.name'],
            cwd=directory,
            capture_output=True,
            text=True
        )
        
        # Check if user email is configured
        email_result = subprocess.run(
            ['git', 'config', 'user.email'],
            cwd=directory,
            capture_output=True,
            text=True
        )
        
        # Set default user name if not configured
        if name_result.returncode != 0:
            subprocess.run(
                ['git', 'config', 'user.name', 'Replit Agent'],
                cwd=directory,
                check=True
            )
        
        # Set default user email if not configured
        if email_result.returncode != 0:
            subprocess.run(
                ['git', 'config', 'user.email', 'agent@replit.com'],
                cwd=directory,
                check=True
            )
    except Exception as e:
        logging.error(f"Error configuring Git user: {str(e)}")
        raise
