import os
from pathlib            import Path
from datetime           import date, datetime
from setup              import pure_uuid_length

def add_spaces(value: str):
    max_length = 5                              # 5 is the maximum length of the given value
    spaces = max_length - len(str(value))
    return ''.ljust(spaces) + str(value)        # ljust -> adds spaces after a string


def initialize_counters():
    """ Initialize variables that will count through the whole task the success of each process """
    
    global_counters = {
        'metadata': { 'success':  0, 'error':    0, },
        'file':     { 'success':  0, 'error':    0, },
        'delete':   { 'success':  0, 'error':    0, },
        'total': 0,
        'http_responses': {}
    }
    return global_counters

def current_time():
    return datetime.now().strftime("%H:%M:%S")


def check_if_directory_exists(directory_name: str):
    
    # Gets synchronizer direcotry path
    dirpath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
    full_path = f'{dirpath}/{directory_name}'

    # If full_path does not exist creates the folder
    Path(full_path).mkdir(parents=True, exist_ok=True)


def check_uuid_authenticity(uuid: str):
    """ Checks if lenght of the uuid is correct """
    if (len(uuid) != pure_uuid_length):
        return False
    return True


