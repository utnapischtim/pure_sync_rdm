

def method_call(docopt_instance: object, arguments: dict):

    if arguments['changes']:
        docopt_instance.changes()

    elif arguments['pages']:
        page_start = int(arguments['PAGE_START'])
        page_end   = int(arguments['PAGE_END'])
        page_size  = int(arguments['PAGE_SIZE'])
        docopt_instance.pages(page_start, page_end, page_size)

    elif arguments['logs']:
        docopt_instance.logs()

    elif arguments['delete']:
        docopt_instance.delete()

    elif arguments['uuid']:
        docopt_instance.uuid()

    elif arguments['duplicates']:
        docopt_instance.duplicates()

    elif arguments['owner']:
        docopt_instance.owner()

    elif arguments['owner_orcid']:
        docopt_instance.owner_orcid()

    elif arguments['owners_list']:
        docopt_instance.owners_list()

    elif arguments['group_split']:
        old_id  = arguments['OLD_GROUP']
        new_ids = arguments['NEW_GROUPS'].split(' ')
        docopt_instance.rdm_group_split(old_id, new_ids)

    elif arguments['group_merge']:
        old_ids = arguments['OLD_GROUPS'].split(' ')
        new_id  = arguments['NEW_GROUP']
        docopt_instance.rdm_group_merge(old_ids, new_id)

