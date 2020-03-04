""" Pure synchronizer

Usage:
    shell_interface.py changes
    shell_interface.py pages
    shell_interface.py shorten_logs
    shell_interface.py delete_from_list
    shell_interface.py push_from_list
    shell_interface.py duplicates
    shell_interface.py delete_all

Options:
    -h --help     Show this screen.
    --version     Show version.

"""
from docopt                         import docopt
import requests
import json
import os
import time
from cmd                            import Cmd
from datetime                       import date, datetime, timedelta
from functions.rdm_push_by_page     import get_pure_by_page

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Pure synchronizer 1.0')
    print(arguments)

if arguments['pages'] == True:
    print('running pages')


class shell_interface ():
    