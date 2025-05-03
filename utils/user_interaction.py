import sys
import os
import getpass
import logging
import readline
import json
from datetime import datetime

class UserInteraction:
    """
    Class for handling user interactions in the terminal.
    """
    
    def __init__(self, history_file='.replit_agent_history'):
        """
        Initialize the UserInteraction class.
        
        Args:
            history_file (str): Path to the history file
        """
        self.history_file = os.path.expanduser(f"~/{history_file}")
        self._load_history()
    
    def _load_history(self):
        """
        Load command history from file.
        """
        try:
            if os.path.exists(self.history_file):
                readline.read_history_file(self.history_file)
                readline.set_history_length(1000)
        except Exception as e:
            logging.warning(f"Error loading history file: {str(e)}")
    
    def _save_history(self):
        """
        Save command history to file.
        """
        try:
            readline.write_history_file(self.history_file)
        except Exception as e:
            logging.warning(f"Error saving history file: {str(e)}")
    
    def prompt(self, message, default=None):
        """
        Prompt the user for input.
        
        Args:
            message (str): Message to display to the user
            default (str, optional): Default value if the user enters nothing
        
        Returns:
            str: User's input, or the default value if none provided
        """
        if default:
            message = f"{message} [{default}]: "
        else:
            message = f"{message}: "
        
        try:
            user_input = input(message)
            if not user_input and default is not None:
                return default
            return user_input
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return None
        except EOFError:
            print("\nEOF detected. Exiting.")
            sys.exit(0)
        finally:
            self._save_history()
    
    def password_prompt(self, message):
        """
        Prompt the user for a password (input is hidden).
        
        Args:
            message (str): Message to display to the user
        
        Returns:
            str: User's password input
        """
        try:
            return getpass.getpass(f"{message}: ")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return None
        except EOFError:
            print("\nEOF detected. Exiting.")
            sys.exit(0)
    
    def confirm(self, message, default=True):
        """
        Ask the user for confirmation.
        
        Args:
            message (str): Message to display to the user
            default (bool, optional): Default value if the user enters nothing
        
        Returns:
            bool: True if the user confirmed, False otherwise
        """
        default_str = "Y/n" if default else "y/N"
        try:
            response = input(f"{message} [{default_str}]: ").strip().lower()
            if not response:
                return default
            return response[0] == 'y'
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return False
        except EOFError:
            print("\nEOF detected. Exiting.")
            sys.exit(0)
        finally:
            self._save_history()
    
    def select_option(self, message, options, allow_cancel=True):
        """
        Ask the user to select an option from a list.
        
        Args:
            message (str): Message to display to the user
            options (list): List of options to choose from
            allow_cancel (bool, optional): Whether to allow cancelling the selection
        
        Returns:
            any: The selected option, or None if cancelled
        """
        if not options:
            return None
        
        try:
            print(f"{message}:")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            if allow_cancel:
                print("  0. Cancel")
            
            while True:
                try:
                    choice = input("Enter your choice: ")
                    if not choice and allow_cancel:
                        return None
                    
                    index = int(choice)
                    if index == 0 and allow_cancel:
                        return None
                    
                    if 1 <= index <= len(options):
                        return options[index - 1]
                    else:
                        print(f"Please enter a number between 1 and {len(options)}")
                except ValueError:
                    print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return None
        except EOFError:
            print("\nEOF detected. Exiting.")
            sys.exit(0)
        finally:
            self._save_history()
    
    def multi_select(self, message, options, default_selected=None):
        """
        Ask the user to select multiple options from a list.
        
        Args:
            message (str): Message to display to the user
            options (list): List of options to choose from
            default_selected (list, optional): List of indices that are selected by default
        
        Returns:
            list: List of selected options
        """
        if not options:
            return []
        
        if default_selected is None:
            default_selected = []
        
        try:
            print(f"{message}:")
            for i, option in enumerate(options, 1):
                selected = i in default_selected or (i-1) in default_selected
                marker = "*" if selected else " "
                print(f"  {i}. [{marker}] {option}")
            
            print("\nEnter numbers to toggle selection, 'a' to select all, 'n' to select none, or 'd' when done")
            
            selected = set(default_selected)
            while True:
                choice = input("Choice: ").strip().lower()
                
                if choice == 'd':
                    # Convert to 0-based indices
                    selected_adjusted = {i-1 if i > 0 else i for i in selected}
                    return [options[i] for i in sorted(selected_adjusted) if 0 <= i < len(options)]
                elif choice == 'a':
                    selected = set(range(1, len(options) + 1))
                    self._display_multi_select(options, selected)
                elif choice == 'n':
                    selected = set()
                    self._display_multi_select(options, selected)
                else:
                    try:
                        index = int(choice)
                        if 1 <= index <= len(options):
                            if index in selected:
                                selected.remove(index)
                            else:
                                selected.add(index)
                            self._display_multi_select(options, selected)
                        else:
                            print(f"Please enter a number between 1 and {len(options)}")
                    except ValueError:
                        print("Please enter a valid option")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return []
        except EOFError:
            print("\nEOF detected. Exiting.")
            sys.exit(0)
        finally:
            self._save_history()
    
    def _display_multi_select(self, options, selected):
        """
        Display the current selection state.
        
        Args:
            options (list): List of options
            selected (set): Set of selected indices
        """
        print("\nCurrent selection:")
        for i, option in enumerate(options, 1):
            marker = "*" if i in selected else " "
            print(f"  {i}. [{marker}] {option}")
    
    def progress(self, message, total):
        """
        Create a progress bar.
        
        Args:
            message (str): Message to display
            total (int): Total number of items
        
        Returns:
            callable: Function to update the progress
        """
        from tqdm import tqdm
        return tqdm(total=total, desc=message, unit='items')
    
    def log_interaction(self, action, details=None, log_file='.replit_agent_log.jsonl'):
        """
        Log user interactions to a file.
        
        Args:
            action (str): The action performed
            details (dict, optional): Additional details about the action
            log_file (str): Path to the log file
        """
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': action
            }
            
            if details:
                log_entry['details'] = details
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logging.warning(f"Error logging interaction: {str(e)}")
    
    def clear_screen(self):
        """
        Clear the terminal screen.
        """
        os.system('cls' if os.name == 'nt' else 'clear')

# Create a global instance for easy access
ui = UserInteraction()

# Standalone functions that use the global instance
def prompt(message, default=None):
    return ui.prompt(message, default)

def password_prompt(message):
    return ui.password_prompt(message)

def confirm(message, default=True):
    return ui.confirm(message, default)

def select_option(message, options, allow_cancel=True):
    return ui.select_option(message, options, allow_cancel)

def multi_select(message, options, default_selected=None):
    return ui.multi_select(message, options, default_selected)

def progress(message, total):
    return ui.progress(message, total)

def log_interaction(action, details=None):
    return ui.log_interaction(action, details)

def clear_screen():
    return ui.clear_screen()
