# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class WorkflowActionRule(models.Model):
    _name = "prescriptions.workflow.rule"
    _description = "A set of condition and actions which will be available to all attachments matching the conditions"
    _order = "sequence"

    domain_folder_id = fields.Many2one('prescriptions.folder', string="Related Workspace", required=True, ondelete='cascade')
    name = fields.Char(required=True, string="Action Button Name", translate=True)
    note = fields.Char(string="Tooltip")
    sequence = fields.Integer('Sequence', default=10)

    # Conditions
    condition_type = fields.Selection([
        ('criteria', "Criteria"),
        ('domain', "Domain"),
    ], default='criteria', string="Condition type")

    # Domain
    domain = fields.Char()

    # Criteria
    criteria_partner_id = fields.Many2one('res.partner', string="Contact")
    criteria_owner_id = fields.Many2one('res.users', string="Owner")
    required_tag_ids = fields.Many2many('prescriptions.tag', 'required_tag_ids_rule_table', string="Required Tags")
    excluded_tag_ids = fields.Many2many('prescriptions.tag', 'excluded_tag_ids_rule_table', string="Excluded Tags")
    limited_to_single_record = fields.Boolean(string="One record limit", compute='_compute_limited_to_single_record')

    # Actions
    partner_id = fields.Many2one('res.partner', string="Set Contact")
    user_id = fields.Many2one('res.users', string="Set Owner")
    tag_action_ids = fields.One2many('prescriptions.workflow.action', 'workflow_rule_id', string='Set Tags')
    folder_id = fields.Many2one('prescriptions.folder', string="Move to Workspace")
    create_model = fields.Selection([('link.to.record', 'Link to record')], string="Create")
    link_model = fields.Many2one('ir.model', string="Specific Model Linked",
                                 domain=[('model', '!=', 'prescriptions.prescription'), ('is_mail_thread', '=', 'True')])

    # Activity
    remove_activities = fields.Boolean(string='Mark all as Done')
    activity_option = fields.Boolean(string='Schedule Activity')
    activity_type_id = fields.Many2one('mail.activity.type', string="Activity type")
    activity_summary = fields.Char('Summary')
    activity_date_deadline_range = fields.Integer(string='Due Date In')
    activity_date_deadline_range_type = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ], string='Due type', default='days')
    activity_note = fields.Html(string="Activity Note")
    has_owner_activity = fields.Boolean(string="Set the activity on the prescription owner")
    activity_user_id = fields.Many2one('res.users', string='Responsible')

    @api.onchange('domain_folder_id')
    def _on_domain_folder_id_change(self):
        if self.domain_folder_id != self.required_tag_ids.mapped('folder_id'):
            self.required_tag_ids = False
        if self.domain_folder_id != self.excluded_tag_ids.mapped('folder_id'):
            self.excluded_tag_ids = False

    def _compute_limited_to_single_record(self):
        """
        Overwritten by bridge modules to define whether the rule is only available for one record at a time.
        """
        self.update({'limited_to_single_record': False})

    def create_record(self, prescriptions=None):
        """
        implemented by each link module to define specific fields for the new business model (create_values)

        When creating/copying/writing an ir.attachment with a res_model and a res_id, add no_prescription=True
        to the context to prevent the automatic creation of a prescription.

        :param prescriptions: the list of the prescriptions of the selection
        :return: the action dictionary that will be called after the workflow action is done or True.
        """
        self.ensure_one()
        if self.create_model == 'link.to.record':
            return self.link_to_record(prescriptions)

        return True

    def link_to_record(self, prescriptions=None):
        """
        :param prescriptions: the list of the prescriptions of the selection
        :return: the action dictionary that will activate a wizard to create a link between the prescriptions of the selection and a record.
        """
        context = {
                    'default_prescription_ids': prescriptions.ids,
                    'default_resource_ref': False,
                    'default_is_readonly_model': False,
                    'default_model_ref': False,
                    }

        prescriptions_link_record = [d for d in prescriptions if (d.res_model != 'prescriptions.prescription')]
        if prescriptions_link_record:
            return {
                    'warning': {
                            'title': _("Already linked Prescriptions"),
                            'prescriptions': [d.name for d in prescriptions_link_record],
                            }
                    }
        elif self.link_model:
            # Throw a warning if the user does not have access to the model.
            self.env[self.link_model.model].check_access_rights('write')
            context['default_is_readonly_model'] = True
            context['default_model_id'] = self.link_model.id

        link_to_record_action = {
                'name': _('Choose a record to link'),
                'type': 'ir.actions.act_window',
                'res_model': 'prescriptions.link_to_record_wizard',
                'view_mode': 'form',
                'target': 'new',
                'views': [(False, "form")],
                'context': context,
            }
        return link_to_record_action

    @api.model
    def unlink_record(self, prescription_ids=None):
        """
        Removes the link with its record for all the prescriptions having is id in prescription_ids
        """
        prescriptions = self.env['prescriptions.prescription'].browse(prescription_ids)
        prescriptions.write({
            'res_model': 'prescriptions.prescription',
            'res_id': False,
            'is_editable_attachment': False,
        })

    def apply_actions(self, prescription_ids):
        """
        called by the front-end Prescription Inspector to apply the actions to the selection of ID's.

        :param prescription_ids: the list of prescriptions to apply the action.
        :return: if the action was to create a new business object, returns an action to open the view of the
                newly created object, else returns True.
        """
        prescriptions = self.env['prescriptions.prescription'].browse(prescription_ids)

        # partner/owner/share_link/folder changes
        prescription_dict = {}
        if self.user_id:
            prescription_dict['owner_id'] = self.user_id.id
        if self.partner_id:
            prescription_dict['partner_id'] = self.partner_id.id
        if self.folder_id:
            prescription_dict['folder_id'] = self.folder_id.id

        # Use sudo if user has write access on prescription else allow to do the
        # other workflow actions(like: schedule activity, send mail etc...)
        try:
            prescriptions.check_access_rights('write')
            prescriptions.check_access_rule('write')
            prescriptions = prescriptions.sudo()
        except AccessError:
            pass

        prescriptions.write(prescription_dict)

        for prescription in prescriptions:
            if self.remove_activities:
                prescription.activity_ids.action_feedback(
                    feedback="completed by rule: %s. %s" % (self.name, self.note or '')
                )

            # tag and facet actions
            for tag_action in self.tag_action_ids:
                tag_action.execute_tag_action(prescription)

        if self.activity_option and self.activity_type_id:
            prescriptions.prescriptions_set_activity(settings_record=self)

        if self.create_model:
            return self.with_company(prescriptions.company_id).create_record(prescriptions=prescriptions)

        return True
