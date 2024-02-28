# -*- coding: utf-8 -*-

from ast import literal_eval

from odoo import models, fields, api, exceptions
from odoo.tools.translate import _
from odoo.tools import consteq

from odoo.osv import expression

import uuid


class PrescriptionShare(models.Model):
    _name = 'prescriptions.share'
    _inherit = ['mail.thread', 'mail.alias.mixin']
    _description = 'Prescriptions Share'

    folder_id = fields.Many2one('prescriptions.folder', string="Workspace", required=True, ondelete='cascade')
    include_sub_folders = fields.Boolean()
    name = fields.Char(string="Name")

    access_token = fields.Char(required=True, default=lambda x: str(uuid.uuid4()), groups="prescriptions.group_prescriptions_user")
    full_url = fields.Char(string="URL", compute='_compute_full_url')
    links_count = fields.Integer(string="Number of Links", compute='_compute_links_count')
    date_deadline = fields.Date(string="Valid Until")
    state = fields.Selection([
        ('live', "Live"),
        ('expired', "Expired"),
    ], default='live', compute='_compute_state', string="Status")
    can_upload = fields.Boolean(compute='_compute_can_upload')

    type = fields.Selection([
        ('ids', "Prescription list"),
        ('domain', "Domain"),
    ], default='ids', string="Share type")
    # type == 'ids'
    prescription_ids = fields.Many2many('prescriptions.prescription', string='Shared Prescriptions')
    # type == 'domain'
    domain = fields.Char()

    action = fields.Selection([
        ('download', "Download"),
        ('downloadupload', "Download and Upload"),
    ], default='download', string="Allows to", inverse="_inverse_action")
    tag_ids = fields.Many2many('prescriptions.tag', string="Shared Tags")
    partner_id = fields.Many2one('res.partner', string="Contact")
    owner_id = fields.Many2one('res.partner', string="Prescription Owner", default=lambda self: self.env.user.partner_id.id)
    email_drop = fields.Boolean(compute='_compute_email_drop', string='Upload by Email', store=True, readonly=False)

    # Activity
    activity_option = fields.Boolean(string='Create a new activity')
    activity_type_id = fields.Many2one('mail.activity.type', string="Activity type")
    activity_summary = fields.Char('Summary')
    activity_date_deadline_range = fields.Integer(string='Due Date In')
    activity_date_deadline_range_type = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ], string='Due type', default='days')
    activity_note = fields.Html(string="Note")
    activity_user_id = fields.Many2one('res.users', string='Responsible')

    _sql_constraints = [
        ('share_unique', 'unique (access_token)', "This access token already exists"),
    ]

    def _compute_display_name(self):
        for record in self:
            record.display_name = record.name or "unnamed link"

    def _get_prescriptions_domain(self):
        """
            Allows overriding the domain in customizations for modifying the search() domain
        """
        if self.type == 'ids':
            return []
        elif self.include_sub_folders:
            return [[('folder_id', 'child_of', self.folder_id.id)]]
        else:
            return [[('folder_id', '=', self.folder_id.id)]]

    def _get_prescriptions(self, prescription_ids=None):
        """
        :param list[int] prescription_ids: limit to the list of prescriptions to fetch.
        :return: recordset of the prescriptions that can be accessed by the create_uid based on the settings
        of the share link.
        """
        self.ensure_one()
        limited_self = self.with_user(self.create_uid)
        Prescriptions = limited_self.env['prescriptions.prescription']

        search_ids = set()
        domains = self._get_prescriptions_domain()

        if prescription_ids is not None:
            if not prescription_ids:
                return Prescriptions
            search_ids = set(prescription_ids)

        if self.type == 'domain':
            record_domain = []
            if self.domain:
                record_domain = literal_eval(self.domain)
            domains.append(record_domain)
            if self.action == 'download':
                domains.append([('type', '!=', 'empty')])
        else:
            share_ids = limited_self.prescription_ids.ids
            search_ids = search_ids.intersection(share_ids) if search_ids else share_ids

        if search_ids or self.type != 'domain':
            domains.append([('id', 'in', list(search_ids))])

        search_domain = expression.AND(domains)
        return Prescriptions.search(search_domain)

    def _get_writable_prescriptions(self, prescriptions):
        """

        :param prescriptions:
        :return: the recordset of prescriptions for which the create_uid has write access
        False only if no write right.
        """
        self.ensure_one()
        try:
            # checks the rights first in case of empty recordset
            prescriptions.with_user(self.create_uid).check_access_rights('write')
        except exceptions.AccessError:
            return False
        return prescriptions.with_user(self.create_uid)._filter_access_rules('write')

    def _check_token(self, access_token):
        if not access_token:
            return False
        try:
            return consteq(access_token, self.access_token)
        except:
            return False

    def _get_prescriptions_and_check_access(self, access_token, prescription_ids=None, operation='write'):
        """
        :param str access_token: the access_token to be checked with the share link access_token
        :param list[int] prescription_ids: limit to the list of prescriptions to fetch and check from the share link.
        :param str operation: access right to check on prescriptions (read/write).
        :return: Recordset[prescriptions.prescription]: all the accessible requested prescriptions
        False if it fails access checks: False always means "no access right", if there are no prescriptions but
        the rights are valid, it still returns an empty recordset.
        """
        self.ensure_one()
        if not self._check_token(access_token):
            return False
        if self.state == 'expired':
            return False
        prescriptions = self._get_prescriptions(prescription_ids)
        if operation == 'write':
            return self._get_writable_prescriptions(prescriptions)
        else:
            return prescriptions

    def _compute_can_upload(self):
        for record in self:
            folder = record.folder_id
            folder_has_groups = folder.group_ids.ids or folder.read_group_ids.ids
            in_write_group = set(folder.group_ids.ids) & set(record.create_uid.groups_id.ids)
            record.can_upload = in_write_group or not folder_has_groups

    def _compute_state(self):
        """
        changes the state based on the expiration date,
         an expired share link cannot be used to upload or download files.
        """
        for record in self:
            record.state = 'live'
            if record.date_deadline:
                today = fields.Date.from_string(fields.Date.today())
                exp_date = fields.Date.from_string(record.date_deadline)
                diff_time = (exp_date - today).days
                if diff_time <= 0:
                    record.state = 'expired'

    @api.depends('action', 'alias_name')
    def _compute_email_drop(self):
        for record in self:
            record.email_drop = record.action == 'downloadupload' and bool(record.alias_name)

    @api.depends('access_token')
    def _compute_full_url(self):
        for record in self:
            record.full_url = (f'{record.get_base_url()}/prescription/share/'
                               f'{record._origin.id or record.id}/{record.access_token}')

    @api.depends('type', 'prescription_ids', 'domain')
    def _compute_links_count(self):
        domains = [record._get_prescriptions_domain()[0] for record in self if record.type == "domain"]
        prescriptions_from_domain = self.env['prescriptions.prescription'].search(expression.OR(domains))

        for record in self:
            prescriptions = []
            if record.type == "ids":
                prescriptions = record.prescription_ids
            elif record.type == "domain":
                prescriptions = prescriptions_from_domain.filtered_domain(record._get_prescriptions_domain()[0])
            record.links_count = sum(1 for prescription in prescriptions if prescription.type == 'url')

    def _inverse_action(self):
        # Prevent the alias from existing if the option is removed
        for record in self:
            if record.action != 'downloadupload' and record.alias_name:
                record.alias_name = False

    def _alias_get_creation_values(self):
        values = super(PrescriptionShare, self)._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('prescriptions.prescription').id
        if self.id:
            values['alias_defaults'] = defaults = literal_eval(self.alias_defaults or "{}")
            defaults.update({
                'tag_ids': [(6, 0, self.tag_ids.ids)],
                'folder_id': self.folder_id.id,
                'partner_id': self.partner_id.id,
                'create_share_id': self.id,
            })
        return values

    def _get_share_popup(self, context, vals):
        view_id = self.env.ref('prescriptions.share_view_form_popup').id
        return {
            'context': context,
            'res_model': 'prescriptions.share',
            'target': 'new',
            'name': _('Share selected files') if vals.get('type') == 'ids' else _('Share selected workspace'),
            'res_id': self.id if self else False,
            'type': 'ir.actions.act_window',
            'views': [[view_id, 'form']], 
        }

    def send_share_by_mail(self, template_xmlid):
        self.ensure_one()
        request_template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if request_template:
            self.message_mail_with_source(request_template)

    @api.model
    def open_share_popup(self, vals):
        """
        returns a view.
        :return: a form action that opens the share window to display the settings.
        """
        new_context = dict(self.env.context)
        # TOOD: since the share is created directly do we really need to set the context?
        new_context.update({
            'default_owner_id': self.env.user.partner_id.id,
            'default_folder_id': vals.get('folder_id'),
            'default_tag_ids': vals.get('tag_ids'),
            'default_type': vals.get('type', 'domain'),
            'default_domain': vals.get('domain') if vals.get('type', 'domain') == 'domain' else False,
            'default_prescription_ids': vals.get('prescription_ids', False),
        })
        return self.create(vals)._get_share_popup(new_context, vals)

    @api.model
    def action_get_share_url(self, vals):
        """
        Creates a new share directly and return it's url
        """
        return self.create(vals).full_url

    def action_delete_shares(self):
        self.unlink()
