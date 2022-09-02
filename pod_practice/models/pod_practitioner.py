

from odoo import api, fields, models, modules


class PodPractitioner(models.Model):
    _name = 'pod.practitioner'
    _description = 'Pod Practitioner'
    _inherit = 'pod.abstract_entity'
    _sql_constraints = [(
        'pod_practitioner_unique_code',
        'UNIQUE (code)',
        'Internal ID must be unique',
    )]

    pod_center_primary_id = fields.Many2one(
        string='Primary pod center',
        comodel_name='medical.center',
    )
#    pod_center_secondary_ids = fields.Many2many(
#        string='Secondary pod center',
#        comodel_name='medical.center',
#    )
    code = fields.Char(
        string='Internal ID',
        help='Unique ID for this professional',
        required=True,
        default=lambda s: s.env['ir.sequence'].next_by_code(s._name + '.code'),
    )
    role_ids = fields.Many2many(
        string='Roles',
        comodel_name='pod.role',
    )
    practitioner_type = fields.Selection(
        [
            ('internal', 'Internal Entity'),
            ('external', 'External Entity')
        ],
        string='Entity Type',
    )
    specialty_id = fields.Many2one(
        string="Main specialty",
        comodel_name='pod.specialty',
    )
    specialty_ids = fields.Many2many(
        string='Other specialties',
        comodel_name='pod.specialty'
    )
    info = fields.Text(string='Extra info')

    @api.model
    def _get_default_image_path(self, vals):
        res = super(PodPractitioner,
                    self)._get_default_image_path(vals)
        if res:
            return res

        practitioner_gender = vals.get('gender', 'male')
        if practitioner_gender == 'other':
            practitioner_gender = 'male'

        image_path = modules.get_module_resource(
            'pod_practitioner',
            'static/src/img',
            'practitioner-%s-avatar.png' % practitioner_gender,
        )
        return image_path


# class PodPatientDisease(models.Model):
#    _name = 'pod.patient_disease'
#    _inherit = 'pod.patient_disease'
#
#    practitioner_id = fields.Many2one(
#        comodel_name='pod.practitioner',
#        string='Physician', index=True
#    )
