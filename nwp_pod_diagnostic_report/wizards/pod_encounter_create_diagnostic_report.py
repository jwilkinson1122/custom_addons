

from odoo import fields, models


class PodiatryEncounterCreateDiagnosticReport(models.TransientModel):

    _inherit = "pod.encounter.create.diagnostic.report"

    template_id = fields.Many2one(
        domain="['|','&', ('template_type','=','general'), "
        "'|', ('pod_department_id','=',False), "
        "('pod_department_id.user_ids','=',uid),"
        "'&', ('create_uid','=',uid), ('template_type', '=', 'user')]"
    )
