""" Pure synchronizer

Usage:
    shell_interface.py changes
    shell_interface.py pages        [--pageStart=<page>, --pageEnd=<page>, --pageSize=<page>]
    shell_interface.py logs
    shell_interface.py delete
    shell_interface.py uuid
    shell_interface.py duplicates
    shell_interface.py owner
    shell_interface.py owner_orcid
    shell_interface.py owners_list
    shell_interface.py group_split [--oldGroup=<recid>, --newGroups=<recid>]
    shell_interface.py group_merge [--oldGroups=<recid>, --newGroup=<recid>]

Arguments:
    OLD_GROUP       Old group externalId (str)
    NEW_GROUPS      List of new groups externalIds separated by a space(str)
    OLD_GROUPS      List of old groups externalIds separated by a space (str)
    NEW_GROUP       New group externalId (str)

Options:
    --pageStart=<page>      Initial page [default:  1].
    --pageEnd=<page>        Ending page  [default:  2].
    --pageSize=<page>       Page size    [default: 10].
    --oldGroup=<recid>      Old group externalId.
    --newGroups=<recid>     List of new groups externalIds separated by a space.
    --oldGroups=<recid>     List of old groups externalIds separated by a space.
    --newGroup=<recid>      New group externalId.
    -h --help               Show this screen.
    --version               Show version.
"""
from docopt                         import docopt
from cli                            import ShellInterface, method_call

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Pure synchronizer 1.0')
    # print(arguments)

    # Create new instance
    docopt_instance = ShellInterface()

# Calls the method given in the arguments
method_call(docopt_instance, arguments)
