from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class PrescriptionOrder(models.Model):
    _inherit = "prescription.order"

    note_header = fields.Html(translate=False)
    note_footer = fields.Html(translate=False)
