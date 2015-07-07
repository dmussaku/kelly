from permission.logics import AuthorPermissionLogic
from permission.logics import CollaboratorsPermissionLogic

PERMISSION_LOGICS = (
    ('alm_crm.Contact', AuthorPermissionLogic()),
    ('alm_crm.Contact', CollaboratorsPermissionLogic()),
    ('alm_vcard.VCard', AuthorPermissionLogic()),
    ('alm_vcard.VCard', CollaboratorsPermissionLogic()),
)