

from odoo import api, fields, models
# from odoo.modules import get_module_resource
from odoo.exceptions import ValidationError


class PodPatient(models.Model):
    _name = 'pod.patient'
    _description = 'Patient'
    _inherit = 'pod.abstract_entity'

    identification_code = fields.Char(
        string='Identificación interna',
        help='Identificación del paciente provista por el centro de salud',
    )
    general_info = fields.Text(
        string='Información General',
    )

    medical_summary = fields.Text(
        'Health conditions related to this patient',
        help='Automated summary of patient health conditions ')
    general_info = fields.Text(
        'Free text information not included in the automatic summary',
        help='Write any important information on the patient\'s condition,'
        ' surgeries, pathologies, ...')

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

    # def _get_default_image_path(self, vals):
    #     super(PodPatient, self)._get_default_image_path(vals)
    #     return get_module_resource(
    #         'pod', 'static/src/img', 'patient-avatar.png'
    #     )

    # def toggle_is_pregnant(self):
    #     self.toggle('is_pregnant')

    # def toggle_safety_cap_yn(self):
    #     self.toggle('safety_cap_yn')

    # def toggle_counseling_yn(self):
    #     self.toggle('counseling_yn')
