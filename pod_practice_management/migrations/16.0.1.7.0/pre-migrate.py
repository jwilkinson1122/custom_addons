import openupgradelib.openupgrade as ou
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ou.delete_records_safely_by_xml_id(
        env,
        [
            "pod_practice_management.restrict_team_access_to_allowed_internal_users",
            "pod_practice_management.restrict_patient_access_to_allowed_internal_users",
            "pod_practice_management.restrict_injury_access_to_allowed_internal_users",
        ],
    )
