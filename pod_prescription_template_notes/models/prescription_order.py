from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class PrescriptionOrder(models.Model):
    _inherit = "prescription.order"

    @api.onchange('prescription_order_template_id')
    def onchange_prescription_order_template_id(self):
        res = super(PrescriptionOrder, self).onchange_prescription_order_template_id()
        # if notes are set in template overwrite the order notes
        if self.prescription_order_template_id.note_header:
            self.note_header = self.prescription_order_template_id.note_header
        if self.prescription_order_template_id.note_footer:
            self.note_footer = self.prescription_order_template_id.note_footer
        return res