# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

from invenio_indexer.api import RecordIndexer
from invenio_records_files.api import Record

from invenio_records_permissions import record_create_permission_factory, \
                                        record_delete_permission_factory, \
                                        record_files_permission_factory, \
                                        record_list_permission_factory, \
                                        record_read_permission_factory, \
                                        record_update_permission_factory

from invenio_records_permissions.api import RecordsSearch
from invenio_records_rest.facets import terms_filter

from invenio_rdm_records.managers_group import OwnerManagerRecordsSearch, owner_manager_permission_factory

def _(x):
    """Identity function for string extraction."""
    return x


# Records REST API endpoints.

RECORDS_REST_ENDPOINTS = dict(
    recid=dict(
        pid_type='recid',
        pid_minter='recid_v2',
        pid_fetcher='recid_v2',
        default_endpoint_prefix=True,
        # search_class=RecordsSearch,
        search_class=OwnerManagerRecordsSearch,
        indexer_class=RecordIndexer,
        record_class=Record,
        search_index='records',
        search_type=None,
        record_serializers={
            'application/json': ('invenio_rdm_records.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('invenio_rdm_records.serializers'
                                 ':json_v1_search'),
        },
        record_loaders={
            'application/json': ('invenio_rdm_records.loaders'
                                 ':json_v1'),
        },
        list_route='/records/',
        item_route='/records/<pid(recid,'
                   'record_class="invenio_records_files.api.Record")'
                   ':pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        error_handlers=dict(),

        read_permission_factory_imp=owner_manager_permission_factory,
        # read_permission_factory_imp=record_read_permission_factory,
        list_permission_factory_imp=record_list_permission_factory,
        create_permission_factory_imp=record_create_permission_factory,
        update_permission_factory_imp=record_update_permission_factory,
        delete_permission_factory_imp=record_delete_permission_factory,

        links_factory_imp='invenio_rdm_records.links.links_factory'
    ),
)

"""REST API for invenio_rdm_records."""

RECORDS_REST_FACETS = dict(
    records=dict(
        aggs=dict(
            access_right=dict(terms=dict(field='access_right')),
            resource_type=dict(terms=dict(field='resource_type.type'))
        ),
        post_filters=dict(
            access_right=terms_filter('access_right'),
            resource_type=terms_filter('resource_type.type')
        )
    )
)
"""Introduce searching facets."""


RECORDS_REST_SORT_OPTIONS = dict(
    records=dict(
        bestmatch=dict(
            title=_('Best match'),
            fields=['_score'],
            default_order='desc',
            order=1,
        ),
        mostrecent=dict(
            title=_('Most recent'),
            fields=['-_created'],
            default_order='asc',
            order=2,
        ),
    )
)
"""Setup sorting options."""


RECORDS_REST_DEFAULT_SORT = dict(
    records=dict(
        query='bestmatch',
        noquery='mostrecent',
    )
)
"""Set default sorting options."""


# Records Permissions

RECORDS_PERMISSIONS_RECORD_POLICY = (
    'invenio_rdm_records.permissions.RDMRecordPermissionPolicy'
)
"""PermissionPolicy used by permission factories above."""

# Files REST

FILES_REST_PERMISSION_FACTORY = record_files_permission_factory
"""Set default files permission factory."""

# Records Files

RECORDS_FILES_REST_ENDPOINTS = {
    'RECORDS_REST_ENDPOINTS': {
        'recid': '/files',
    }
}
"""Set default files rest endpoints."""

PIDSTORE_RECID_FIELD = 'recid'
