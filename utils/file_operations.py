import os
import shutil
import logging

def list_files(directory='.'):
    """
    List all files and directories in the specified directory.
    
    Args:
        directory (str): Path to the directory to list
    
    Returns:
        list: List of dictionaries containing file information
    """
    try:
        items = []
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            item_type = 'file' if os.path.isfile(path) else 'directory'
            size = os.path.getsize(path) if os.path.isfile(path) else None
            items.append({
                'name': item,
                'path': path,
                'type': item_type,
                'size': size
            })
        return items
    except Exception as e:
        logging.error(f"Error listing files in directory {directory}: {str(e)}")
        raise

def create_file(path, content=''):
    """
    Create a new file with the given content.
    
    Args:
        path (str): Path to the file to create
        content (str): Content to write to the file
    """
    try:
        with open(path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        logging.error(f"Error creating file {path}: {str(e)}")
        raise

def read_file(path):
    """
    Read the contents of a file.
    
    Args:
        path (str): Path to the file to read
    
    Returns:
        str: Contents of the file
    """
    try:
        with open(path, 'r') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try to open as binary if text reading fails
        with open(path, 'rb') as f:
            return "Binary file, cannot display content."
    except Exception as e:
        logging.error(f"Error reading file {path}: {str(e)}")
        raise

def write_file(path, content):
    """
    Write content to a file, overwriting existing content.
    
    Args:
        path (str): Path to the file to write
        content (str): Content to write to the file
    """
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        logging.error(f"Error writing to file {path}: {str(e)}")
        raise

def delete_file(path):
    """
    Delete a file or directory.
    
    Args:
        path (str): Path to the file or directory to delete
    """
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return True
    except Exception as e:
        logging.error(f"Error deleting {path}: {str(e)}")
        raise

def create_directory(path):
    """
    Create a new directory.
    
    Args:
        path (str): Path to the directory to create
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {path}: {str(e)}")
        raise

def copy_file(source, destination):
    """
    Copy a file from source to destination.
    
    Args:
        source (str): Path to the source file
        destination (str): Path to the destination file
    """
    try:
        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(destination)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        logging.error(f"Error copying file from {source} to {destination}: {str(e)}")
        raise

def move_file(source, destination):
    """
    Move a file from source to destination.
    
    Args:
        source (str): Path to the source file
        destination (str): Path to the destination file
    """
    try:
        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(destination)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            
        shutil.move(source, destination)
        return True
    except Exception as e:
        logging.error(f"Error moving file from {source} to {destination}: {str(e)}")
        raise

def get_file_info(path):
    """
    Get information about a file.
    
    Args:
        path (str): Path to the file
    
    Returns:
        dict: Dictionary containing file information
    """
    try:
        stat_info = os.stat(path)
        return {
            'name': os.path.basename(path),
            'path': path,
            'size': stat_info.st_size,
            'created': stat_info.st_ctime,
            'modified': stat_info.st_mtime,
            'is_file': os.path.isfile(path),
            'is_directory': os.path.isdir(path)
        }
    except Exception as e:
        logging.error(f"Error getting file info for {path}: {str(e)}")
        raise

def search_files(directory='.', pattern='*'):
    """
    Search for files matching a pattern in a directory.
    
    Args:
        directory (str): Directory to search in
        pattern (str): Pattern to match against file names
    
    Returns:
        list: List of files matching the pattern
    """
    try:
        import glob
        return glob.glob(os.path.join(directory, pattern))
    except Exception as e:
        logging.error(f"Error searching for files with pattern {pattern} in {directory}: {str(e)}")
        raise
