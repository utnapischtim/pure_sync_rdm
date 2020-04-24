""" Pure synchronizer

Usage:
    shell_interface.py changes
    shell_interface.py pages            (PAGE_START) (PAGE_END) (PAGE_SIZE)
    shell_interface.py logs
    shell_interface.py delete
    shell_interface.py uuid
    shell_interface.py duplicates
    shell_interface.py owner
    shell_interface.py owner_orcid
    shell_interface.py owners_list
    shell_interface.py group_split      (OLD_GROUP) (NEW_GROUPS)
    shell_interface.py group_merge      (OLD_GROUPS) (NEW_GROUP)

Arguments:
    PAGE_START      Starting page (int)
    PAGE_END        Ending page (int)
    PAGE_SIZE       Page size (int)
    OLD_GROUP       Old group externalId (str)
    NEW_GROUPS      List of new groups externalIds separated by a space(str)
    OLD_GROUPS      List of old groups externalIds separated by a space (str)
    NEW_GROUP       New group externalId (str)

Options:
    -h --help     Show this screen.
    --version     Show version.
"""
from docopt                         import docopt
from cli                            import ShellInterface, method_call

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Pure synchronizer 1.0')
    # Create new instance
    docopt_instance = ShellInterface()

# Calls the method given in the arguments
method_call(docopt_instance, arguments)
