

from odoo import api, fields, models
# from odoo.modules import get_module_resource
from odoo.exceptions import ValidationError


class PodPatient(models.Model):
    _name = 'pod.patient'
    _description = 'Patient'
    _inherit = 'pod.abstract_entity'

    identification_code = fields.Char(
        string='Internal Identitfication',
        help='Identification of the patient provided by the health center',
    )
    general_info = fields.Text(
        string='General Information',
    )

    medical_summary = fields.Text(
        'Health conditions related to this patient',
        help='Automated summary of patient health conditions ')
    general_info = fields.Text(
        'Free text information not included in the automatic summary',
        help='Write any important information on the patient\'s condition,'
        ' surgeries, pathologies, ...')

    patient_of_medical_center_id = fields.Many2one(
        string='Medical center',
        comodel_name='medical.center',
    )

#    medical_center_secondary_ids = fields.Many2many(
#        string='Secondary medical center',
#        comodel_name='medical.center',
#    )

    @api.model
    def _create_vals(self, vals):
        vals = super(PodPatient, self)._create_vals(vals)
        if not vals.get('identification_code'):
            Seq = self.env['ir.sequence']
            vals['identification_code'] = Seq.sudo().next_by_code(
                self._name,
            )
        # vals.update({
        #     'customer': True,
        # })
        return vals

    # def toggle_is_pregnant(self):
    #     self.toggle('is_pregnant')

    # def toggle_safety_cap_yn(self):
    #     self.toggle('safety_cap_yn')

    # def toggle_counseling_yn(self):
    #     self.toggle('counseling_yn')
