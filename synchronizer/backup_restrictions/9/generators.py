# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-Records-Permissions is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Invenio Records Permissions Generators."""

import json
import operator
from functools import reduce
from itertools import chain

from elasticsearch_dsl.query import Q
from flask import g
from flask_principal import ActionNeed, UserNeed, RoleNeed
from invenio_access.permissions import any_user, superuser_access
from invenio_files_rest.models import Bucket, ObjectVersion
from invenio_records_files.api import Record
from invenio_records_files.models import RecordsBuckets
from invenio_accounts.ext   import InvenioAccountsREST

# from flask_security import current_user                  ###############################
# from invenio_accounts.models import SessionActivity      ###############################
# from invenio_db import db                                ###############################
# from flask_security.utils import get_identity_attributes ###############################



class Generator(object):
    """Parent class mapping the context when an action is allowed or denied.

    It does so by *generating* "needed" and "excluded" Needs. At the search
    level it implements the *query filters* to restrict the search.

    Any context inherits from this class.
    """

    def needs(self, **kwargs):
        """Enabling Needs."""
        return []

    def excludes(self, **kwargs):
        """Preventing Needs."""
        return []

    def query_filter(self, **kwargs):
        """Elasticsearch filters."""
        return []


class AnyUser(Generator):
    """Allows any user."""

    def __init__(self):
        """Constructor."""
        super(AnyUser, self).__init__()

    def needs(self, **kwargs):
        """Enabling Needs."""
        return [any_user]

    def query_filter(self, **kwargs):
        """Match all in search."""
        # TODO: Implement with new permissions metadata
        return Q('match_all')


class SuperUser(Generator):
    """Allows super users."""

    def __init__(self):
        """Constructor."""
        super(SuperUser, self).__init__()

    def needs(self, **kwargs):
        """Enabling Needs."""
        return [superuser_access]

    def query_filter(self, record=None, **kwargs):
        """Filters for current identity as super user."""
        # TODO: Implement with new permissions metadata
        return []


class Disable(Generator):
    """Denies ALL users including super users."""

    def __init__(self):
        """Constructor."""
        super(Disable, self).__init__()

    def excludes(self, **kwargs):
        """Preventing Needs."""
        return [any_user]

    def query_filter(self, **kwargs):
        """Match None in search."""
        return ~Q('match_all')


class Admin(Generator):
    """Allows users with admin-access (different from superuser-access)."""
    
    def __init__(self):
        """Constructor."""
        super(Admin, self).__init__()

    def needs(self, **kwargs):
        """Enabling Needs."""
        return [ActionNeed('admin-access')]



###   ###   ###   ###   ###   ###
#
class RecordOwners(Generator):
    """Allows record owners."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""

        # Allow access to records with 'owners' in appliedRestrictions
        if 'owners' not in record.get('appliedRestrictions', []):
            return[]
        return [UserNeed(owner) for owner in record.get('owners', [])]

    def query_filter(self, **kwargs):
        """Filters for current identity as owner."""
        
        # Contains logged-in user information
        provides = g.identity.provides
        
        # Specify which restriction will be applied (owners)
        matches = {'appliedRestrictions': 'owners'}

        # Gets the user id
        for need in provides:
            if need.method == 'id':
                matches['owners'] = need.value
                break

        # Queries Elasticsearch -> both user_id and appliedRestrictions need to match
        queries = [
            Q('match', **{
                match: f"{matches[match]}"
            })for match in matches
        ]
        return reduce(operator.and_, queries)

        

class RecordGroups(Generator):
    
    def needs(self, record=None, **rest_over):
        # Allow access to records with 'groups' in appliedRestrictions
        if 'groups' not in record.get('appliedRestrictions', []):
            return[]
        return [RoleNeed(group) for group in record.get('groupRestrictions', [])]

    def query_filter(self, *args, **kwargs):

        # Contains logged-in user information
        provides = g.identity.provides
        
        # Specify which restriction will be applied (groups)
        queries = Q('match', **{"appliedRestrictions": 'groups'})

        # Get all user's groups
        record_groups = []
        for need in provides:
            if need.method == 'role':
                matches['groupRestrictions'] = need.value

        # Queries Elasticsearch:
        #       - appliedRestrictions need to have 'groups'
        #       - at least one group need to match
        queries2 = [
            Q('match', **{
                match: f"{matches[match]}"
            })for match in matches
        ]
        queries += reduce(operator.or_, queries2)
        return queries



class RecordIp (Generator):

    def __init__(self):
        from invenio_records_permissions.setup import single_ips

        # Connects to database
        cursor = database_connect()
        
        # Get user IP address
        cursor.execute("SELECT ip FROM accounts_user_session_activity;")
        user_ip = cursor.fetchall()[0][0]

        # single_ips = ['127.0.0.3', '127.0.0.8']           # TEMP
        self.visible = False

        # Checks if the user IP is among single IPs
        if user_ip in single_ips:
            self.visible = True

    def needs(self, record=None, **rest_over):
        # Allow access to records with 'ip_single' in appliedRestrictions
        if 'ip_single' in record.get('appliedRestrictions', []) and self.visible:
            return [any_user]
        return[]
            
    def query_filter(self, *args, **kwargs):
        if self.visible:
            return Q('match', **{"appliedRestrictions": "ip_single"})
        return ~Q('match_all')

class RecordIpRange (Generator):
    """
    Allows access: 
        - when 'ip_ranges' is in appliedRestrictions field
        - when the user_ip is in ip_range
    """

    def __init__(self):
        from invenio_records_permissions.setup import ip_ranges

        # Connects to database
        cursor = database_connect()
        
        # Get user IP address
        cursor.execute("SELECT ip FROM accounts_user_session_activity;")
        user_ip = cursor.fetchall()[0][0]

        # user_ip = '127.0.0.4'         # TEMP
        self.visible = False

        # Checks if the user IP is in an IP range
        for ip_range in ip_ranges:
            ip_start = ip_range[0]
            ip_end   = ip_range[1]
            if user_ip >= ip_start and user_ip <= ip_end:
                self.visible = True

    def needs(self, record=None, **rest_over):
        # Checks if 'ip_ranges' is in appliedRestrictions
        if 'ip_ranges' in record.get('appliedRestrictions', []) and self.visible:
            return [any_user]
        return[]

    def query_filter(self, *args, **kwargs):
        if self.visible:
            return Q('match', **{"appliedRestrictions": 'ip_ranges'})

        # Match None in search
        return ~Q('match_all')

#
###   ###   ###   ###   ###   ###


class AnyUserIfPublic(Generator):
    """Allows any user if record is public.

    TODO: Revisit when dealing with files.
    """

    def needs(self, record=None, **rest_over):
        """Enabling Needs."""
        is_restricted = (
            record and
            record.get('_access', {}).get('metadata_restricted', False)
        )
        return [any_user] if not is_restricted else []

    def excludes(self, record=None, **rest_over):
        """Preventing Needs."""
        return []

    def query_filter(self, *args, **kwargs):
        """Filters for non-restricted records."""
        # TODO: Implement with new permissions metadata
        return Q('term', **{"_access.metadata_restricted": False})


class AllowedByAccessLevel(Generator):
    """Allows users/roles/groups that have an appropriate access level."""

    # TODO: Implement other access levels:
    # 'metadata_reader'
    # 'files_reader'
    # 'files_curator'
    # 'admin'
    ACTION_TO_ACCESS_LEVELS = {
        'create': [],
        'read': ['metadata_curator'],
        'update': ['metadata_curator'],
        'delete': []
    }

    def __init__(self, action='read'):
        """Constructor."""
        self.action = action

    def needs(self, record=None, **kwargs):
        """Enabling UserNeeds for each person."""
        if not record:
            return []

        access_levels = AllowedByAccessLevel.ACTION_TO_ACCESS_LEVELS.get(
            self.action, [])

        # Name "identity" is used bc it correlates with flask-principal
        # identity while not being one.
        allowed_identities = chain.from_iterable([
            record.get('internal', {})
                  .get('access_levels', {})
                  .get(access_level, [])
            for access_level in access_levels
        ])

        return [
            UserNeed(identity.get('id')) for identity in allowed_identities
            if identity.get('scheme') == 'person' and identity.get('id')
            # TODO: Implement other schemes
        ]

    def query_filter(self, *args, **kwargs):
        """Search filter for the current user with this generator."""
        id_need = next(
            (need for need in g.identity.provides if need.method == 'id'),
            None
        )

        if not id_need:
            return []

        # To get the record in the search results, the access level must
        # have been put in the 'read' array
        read_levels = AllowedByAccessLevel.ACTION_TO_ACCESS_LEVELS.get(
            'read', [])

        queries = [
            Q('term', **{
                "internal.access_levels.{}".format(access_level): {
                    "scheme": "person", "id": id_need.value
                    # TODO: Implement other schemes
                }
            }) for access_level in read_levels
        ]

        return reduce(operator.or_, queries)

#
# | Meta Restricted | Files Restricted | Access Right | Result |
# |-----------------|------------------|--------------|--------|
# |       True      |       True       |   Not Open   |  False |
# |-----------------|------------------|--------------|--------|
# |       True      |       True       |     Open     |  False | # Inconsistent
# |-----------------|------------------|--------------|--------|
# |       True      |       False      |   Not Open   |  False | # Inconsistent
# |-----------------|------------------|--------------|--------|
# |       True      |       False      |     Open     |  False | # Inconsistent
# |-----------------|------------------|--------------|--------|
# |       False     |       True       |   Not Open   |  False | ??Inconsistent
# |-----------------|------------------|--------------|--------|
# |       False     |       True       |     Open     |  False |
# |-----------------|------------------|--------------|--------|
# |       False     |       False      |   Not Open   |  False | # Inconsistent
# |-----------------|------------------|--------------|--------|
# |       False     |       False      |     Open     |  True  |
# |-----------------|------------------|--------------|--------|
#

def database_connect():
    from invenio_records_permissions.setup import db_host, db_name, db_user, db_password
    import psycopg2
    connection = psycopg2.connect(f"""\
        host={db_host} \
        dbname={db_name} \
        user={db_user} \
        password={db_password} \
        """)
    return connection.cursor()
    