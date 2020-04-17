
if arguments['changes']:
    docopt_instance.changes()

elif arguments['pages']:
    docopt_instance.pages()

elif arguments['logs']:
    docopt_instance.logs()

elif arguments['delete']:
    docopt_instance.delete()

elif arguments['uuid']:
    docopt_instance.uuid()

elif arguments['duplicates']:
    docopt_instance.duplicates()

elif arguments['delete_all']:
    docopt_instance.delete_all()

elif arguments['owners']:
    docopt_instance.owners()

elif arguments['owners_orcid']:
    docopt_instance.owners_orcid()

elif arguments['owners_list']:
    docopt_instance.owners_list()

elif arguments['group_split']:
    docopt_instance.rdm_group_split()

elif arguments['group_merge']:
    docopt_instance.rdm_group_merge()