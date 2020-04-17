""" Pure synchronizer

Usage:
    shell_interface.py test1 [AAA]
    shell_interface.py test2 (BBB)

Arguments:
    AAA        Not mandatory
    BBB        Mandatory

Options:
    -h --help     Show this screen.
    --version     Show version.

"""

from docopt       import docopt

class shell_interface:
    
    def test1(self, vv):
        vv = vv.split(' ')
        print(vv)

    def test2(self, vv):
        print(vv)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Pure synchronizer 1.0')
    print(arguments)
    docopt_instance = shell_interface()

# import test

if arguments['test1']:
    docopt_instance.test1(arguments['AAA'])

elif arguments['test2']:
    docopt_instance.test2(arguments['BBB'])
