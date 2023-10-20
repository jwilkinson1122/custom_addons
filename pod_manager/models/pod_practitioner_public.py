# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class PodPractitionerPublic(models.Model):
    _name = "pod.practitioner.public"
    _inherit = ["pod.practitioner.base"]
    _description = 'Public Practitioner'
    _order = 'name'
    _auto = False
    _log_access = True # Include magic fields

    # Fields coming from pod.practitioner.base
    create_date = fields.Datetime(readonly=True)
    name = fields.Char(readonly=True)
    active = fields.Boolean(readonly=True)
    practice_id = fields.Many2one(readonly=True)
    role_id = fields.Many2one(readonly=True)
    role_title = fields.Char(readonly=True)
    company_id = fields.Many2one(readonly=True)
    address_id = fields.Many2one(readonly=True)
    mobile_phone = fields.Char(readonly=True)
    practice_phone = fields.Char(readonly=True)
    practice_email = fields.Char(readonly=True)
    practice_location_id = fields.Many2one(readonly=True)
    user_id = fields.Many2one(readonly=True)
    resource_id = fields.Many2one(readonly=True)
    resource_calendar_id = fields.Many2one(readonly=True)
    tz = fields.Selection(readonly=True)
    color = fields.Integer(readonly=True)
    practitioner_type = fields.Selection(readonly=True)

    practitioner_id = fields.Many2one('pod.practitioner', 'Practitioner', compute="_compute_practitioner_id", search="_search_practitioner_id", compute_sudo=True)
    # pod.practitioner.public specific fields
    child_ids = fields.One2many('pod.practitioner.public', 'parent_id', string='Direct subordinates', readonly=True)
    image_1920 = fields.Image("Image", related='practitioner_id.image_1920', compute_sudo=True)
    image_1024 = fields.Image("Image 1024", related='practitioner_id.image_1024', compute_sudo=True)
    image_512 = fields.Image("Image 512", related='practitioner_id.image_512', compute_sudo=True)
    image_256 = fields.Image("Image 256", related='practitioner_id.image_256', compute_sudo=True)
    image_128 = fields.Image("Image 128", related='practitioner_id.image_128', compute_sudo=True)
    avatar_1920 = fields.Image("Avatar", related='practitioner_id.avatar_1920', compute_sudo=True)
    avatar_1024 = fields.Image("Avatar 1024", related='practitioner_id.avatar_1024', compute_sudo=True)
    avatar_512 = fields.Image("Avatar 512", related='practitioner_id.avatar_512', compute_sudo=True)
    avatar_256 = fields.Image("Avatar 256", related='practitioner_id.avatar_256', compute_sudo=True)
    avatar_128 = fields.Image("Avatar 128", related='practitioner_id.avatar_128', compute_sudo=True)
    parent_id = fields.Many2one('pod.practitioner.public', 'Manager', readonly=True)
    assistant_id = fields.Many2one('pod.practitioner.public', 'Assistant', readonly=True)
    user_partner_id = fields.Many2one(related='user_id.partner_id', related_sudo=False, string="User's partner")

    def _search_practitioner_id(self, operator, value):
        return [('id', operator, value)]

    def _compute_practitioner_id(self):
        for practitioner in self:
            practitioner.practitioner_id = self.env['pod.practitioner'].browse(practitioner.id)

    @api.model
    def _get_fields(self):
        return ','.join('emp.%s' % name for name, field in self._fields.items() if field.store and field.type not in ['many2many', 'one2many'])

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT
                %s
            FROM pod_practitioner emp
        )""" % (self._table, self._get_fields()))
