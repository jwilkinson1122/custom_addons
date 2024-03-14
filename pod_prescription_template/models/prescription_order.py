from odoo import fields, models, api, _
import logging
_logger = logging.getLogger(__name__)

class PrescriptionOrder(models.Model):
    _inherit = ['prescription.order']

    prescription_order_template_id = fields.Many2one(
        'prescription.order.template', 'Prescription Template',
        ondelete='cascade', index=True)

    @api.onchange('prescription_order_template_id')
    def onchange_prescription_order_template_id(self):

        # template = self.prescription_order_template_id.with_context(lang=self.partner_id.lang)
        template = self.prescription_order_template_id
        
        if not self.note_header or self.note_header == '<p><br></p>':
            self.note_header = template.note_header

        if not self.note_footer or self.note_footer == '<p><br></p>':
            self.note_footer = template.note_footer