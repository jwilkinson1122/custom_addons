from odoo import api, fields, models, _

class PrescriptionOrderTemplate(models.Model):
    _inherit = "prescription.order.template"

    note_header = fields.Html(translate=False)
    note_footer = fields.Html(translate=False)
