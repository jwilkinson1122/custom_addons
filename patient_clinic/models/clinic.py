from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class Clinic(models.Model):
    _name = 'patient_clinic.clinic'
    _description = "Podiatry Clinic"
    _inherit = ['resource.mixin']
    _order = 'sequence,id'

    _parent_name = 'parent_id'
    _parent_store = True

    parent_path = fields.Char(string="Parent Path", index=True)

    parent_id = fields.Many2one(
        comodel_name='patient_clinic.clinic',
        string="Parent Clinic",
        index=True,
        ondelete='cascade',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    active = fields.Boolean(string="Active", default=True)
    name = fields.Char(string="Clinic Name", index=True, translate=True)
    color = fields.Integer(string="Color Index (0-15)")
    sequence = fields.Integer(
        string="Sequence", required=True,
        default=5,
    )

    code = fields.Char(string="Code", copy=False)
    full_name = fields.Char(
        string="Full Name",
        compute='_compute_full_name',
        store=True,
    )

    @api.depends('name', 'parent_id.full_name')
    def _compute_full_name(self):
        for clinic in self:
            if clinic.parent_id:
                clinic.full_name = "%s / %s" % (
                    clinic.parent_id.full_name, clinic.name)
            else:
                clinic.full_name = clinic.name
        return

    notes = fields.Text(string="Notes")

    patient_id = fields.Many2one(
        comodel_name='patient_clinic.patient',
        string="Patient",
    )

    doctor_id = fields.Many2one(
        comodel_name='patient_clinic.doctor',
        string="Doctor",
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string="User",
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )

    child_ids = fields.One2many(
        comodel_name='patient_clinic.clinic',
        inverse_name='parent_id',
        string="Subclinics",
    )
    child_count = fields.Integer(
        string="Subclinic Count",
        compute='_compute_child_count',
    )

    @api.depends('child_ids')
    def _compute_child_count(self):
        for clinic in self:
            clinic.child_count = len(clinic.child_ids)
        return

    @api.model_create_multi
    def create(self, values):
        return super(Clinic, self.with_context(default_resource_type='material')).create(values)

    def name_get(self):
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super(Clinic, self).name_get()
