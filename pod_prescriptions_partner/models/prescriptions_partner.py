from odoo import models, fields, api, _, Command
from odoo.exceptions import ValidationError


class PrescriptionPartner(models.Model):
    _name = "prescriptions.partner"
    _description = "Prescriptions Partner"

    name = fields.Char()
    patient_ids = fields.Many2many(comodel_name='prescriptions.patient', relation='prescriptions_partner_patient_rel', column1='prescriptions_partner_id', column2='patient_id', string='Patients')
    patient_count = fields.Integer(compute="_compute_patient_counts")
    injured_count = fields.Integer(compute="_compute_patient_counts")
    healthy_count = fields.Integer(compute="_compute_patient_counts")
    parent_id = fields.Many2one(comodel_name='res.partner', string='Parent Company', ondelete='restrict')
    personnel_ids = fields.One2many(comodel_name='prescriptions.partner.personnel', inverse_name='prescriptions_partner_id')
    manager_id = fields.Many2one(comodel_name='res.partner', compute='_compute_manager', store=True)
    manager_name = fields.Char(related='manager_id.name')
    practitioner_id = fields.Many2one(comodel_name='res.partner', compute='_compute_practitioner', store=True)
    practitioner_name = fields.Char(related='practitioner_id.name')
    website = fields.Char()

    @api.depends('patient_ids.is_injured')
    def _compute_patient_counts(self):
        for rec in self:
            rec.patient_count = len(rec.patient_ids)
            rec.injured_count = len(rec.patient_ids.filtered(lambda p: p.is_injured))
            rec.healthy_count = rec.patient_count - rec.injured_count

    @api.depends('personnel_ids.role')
    def _compute_manager(self):
        for rec in self:
            personnel = rec.personnel_ids.filtered(lambda r: r.role == 'manager')
            rec.manager_id = personnel.partner_id if personnel else False

    @api.depends('personnel_ids.role')
    def _compute_practitioner(self):
        for rec in self:
            personnel = rec.personnel_ids.filtered(lambda r: r.role == 'practitioner')
            rec.practitioner_id = personnel.partner_id if personnel else False


class PartnerPersonnel(models.Model):
    _name = "prescriptions.partner.personnel"
    _description = "Relationship between personnel members and their partners."

    sequence = fields.Integer()
    prescriptions_partner_id = fields.Many2one(comodel_name='prescriptions.partner', string='Partner', required=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Personnel Member', required=True, domain=[('is_company', '=', False)])
    role = fields.Selection(selection=[
        ('manager', 'Manager'),
        ('practitioner', 'Practitioner'),
        ('manager', 'Manager'),
        ('assistant', 'Assistant'),
        ('orthotist', 'Orthotist'),
        ('other', 'Other')
    ], required=True)
    mobile = fields.Char(related='partner_id.mobile', readonly=False)
    name = fields.Char(related='partner_id.name', readonly=False)
    parent_id = fields.Many2one(related='partner_id.parent_id', readonly=False, string="Company", domain=[('is_company', '=', True)])
    email = fields.Char(related='partner_id.email', readonly=False)
    user_ids = fields.One2many(related='partner_id.user_ids', readonly=True)
    has_portal_access = fields.Boolean(compute='_compute_has_portal_access', compute_sudo=True)

    _sql_constraints = [('partner_personnel_unique', 'unique(prescriptions_partner_id, partner_id)',
                         'Each partner can only be related to a given partner once.')]

    @api.constrains('role')
    def _constrain_role(self):
        partners = self.mapped('prescriptions_partner_id')
        for partner in partners:
            if len(partner.personnel_ids.filtered(lambda r: r.role == 'manager')) > 1:
                raise ValidationError(_("A partner can have only one manager."))
            if len(partner.personnel_ids.filtered(lambda r: r.role == 'practitioner')) > 1:
                raise ValidationError(_("A partner can have only one practitioner."))

    @api.onchange('mobile')
    def _onchange_mobile_validation(self):
        if self.mobile:
            self.mobile = self.partner_id._phone_format(self.mobile, force_format='INTERNATIONAL')

    @api.depends('user_ids', 'user_ids.groups_id')
    def _compute_has_portal_access(self):
        for rec in self:
            rec.has_portal_access = bool(rec.user_ids.filtered(lambda r: r.has_group('base.group_portal'))) or bool(
                rec.user_ids.filtered(lambda r: r.has_group('base.group_user'))) or bool(rec.partner_id.signup_token)

    def action_revoke_portal_access(self):
        group_portal = self.env.ref('base.group_portal')
        group_public = self.env.ref('base.group_public')
        self.user_ids.write(
            {'groups_id': [Command.unlink(group_portal.id), Command.link(group_public.id)], 'active': False})
        # Remove the signup token, so it cannot be used
        self.partner_id.sudo().signup_token = False

    def action_grant_portal_access(self):
        wiz = self.env['portal.wizard'].create({'partner_ids': [(4, self.partner_id.id)]})
        return wiz._action_open_modal()
