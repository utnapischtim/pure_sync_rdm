from elasticsearch_dsl  import Q
from flask_security     import current_user
from invenio_search.api import DefaultFilter, RecordsSearch
from invenio_access     import Permission
from flask_principal    import UserNeed, RoleNeed


def owner_manager_permission_factory(record=None):
    """Returns permission for managers group."""
    return Permission(UserNeed(record["owner"]), RoleNeed('managers'))

def owner_manager_permission_filter():
    """Search filter with permission."""
    if current_user.has_role('managers'):
        return [Q(name_or_query='match_all')]
    else:
        return [Q('match', owner=current_user.get_id())]

class OwnerManagerRecordsSearch(RecordsSearch):
    """Class providing permission search filter."""

    class Meta:
        index = 'records'
        default_filter = DefaultFilter(owner_manager_permission_filter)
        doc_types = None