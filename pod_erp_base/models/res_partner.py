# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import json
from lxml import etree
from odoo.osv import expression


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'mail.thread', 'mail.activity.mixin']

    street = fields.Char(tracking=True)
    street2 = fields.Char(tracking=True)
    zip = fields.Char(tracking=True)
    city = fields.Char(tracking=True)
    state_id = fields.Many2one('res.country.state', tracking=True)
    country_id = fields.Many2one('res.country', tracking=True)

    
   # Identifier Booleans
    is_patient = fields.Boolean('Patient', tracking=True)
    is_practice = fields.Boolean(string="Practice", tracking=True)
    is_location = fields.Boolean(string="Location", tracking=True)
    is_practitioner = fields.Boolean(string="Practitioner", tracking=True)
    is_personnel = fields.Boolean(string="Personnel", tracking=True)
    is_sales_partner = fields.Boolean(string="Sales Partner", tracking=True)
 
    # company_type = fields.Selection(selection_add=[('location', 'Location')])

    company_type = fields.Selection(string='Company Type',
        selection=[('company', 'Company'), ('person', 'Location')],
        compute='_compute_company_type', inverse='_write_company_type')

    # contact_type_id = fields.Many2one("contact.type",string="Contact Type", tracking=True)
    contact_uuid = fields.Char(string="Contact UUID", index=True)
    record_num = fields.Char(string="Medical Record Number", tracking=True)
    program_group = fields.Char(string="Program Group", tracking=True)
    # program_ids = fields.Many2many("pod.program", "res_partner_program_rel", "partner_id", "program_id", string="Programs", tracking=True)
    # status_ids = fields.Many2one("pod.status", string="Status", tracking=True)
    patient_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender", tracking=True)

    patient_birthday = fields.Date('Date of Birth', tracking=True)
    patient_birthday_str = fields.Char(string='Birthday string', compute='compute_patient_birthday_str', store=True)
    patient_url = fields.Char(string="Patient URL", tracking=True)
    fax = fields.Char(string="Fax", tracking=True)
 
    # Types of contacts
    practice_id = fields.Many2one("res.partner", string="Practice", tracking=True)
    practice_location_id = fields.Many2one("res.partner", string="Practice Location", tracking=True)
    practice_practitioner_id = fields.Many2one("res.partner", string="Practitioner", tracking=True)
    practice_billing_id = fields.Many2one("res.partner", string="Billing", tracking=True)
    practice_assistant_id = fields.Many2one("res.partner", string="Medical Assitant", tracking=True)
    sales_partner_id = fields.Many2one("res.partner", string="Sales Partner", tracking=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Default Warehouse", tracking=True)
    order_uuid = fields.Char(string="Order UUID", index=True)

    _sql_constraints = [("contact_uuid_unique", "unique(contact_uuid)", 'Contact UUID Must be Unique!')]

    @api.depends('patient_birthday')
    def compute_patient_birthday_str(self):
        """
        Compute method to set birthdate as string in new field.
        """
        for partner in self:
            partner.patient_birthday_str = partner.patient_birthday and partner.patient_birthday.strftime("%m/%d/%Y") or ""


    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(ResPartner, self).fields_view_get(view_id=view_id,
    #                                                   view_type=view_type,
    #                                                   toolbar=toolbar,
    #                                                   submenu=submenu)
    #
    #     if self.env.user.has_group('pod_erp_base.group_patient_editable'):
    #         doc = etree.XML(res['arch'])
    #         for field in res['fields']:
    #             for node in doc.xpath("//field[@name='practice_location_id'] \
    #                                 | //field[@name='practice_practitioner_id'] \
    #                                 | //field[@name='practice_assistant_id'] \
    #                                 | //field[@name='practice_id'] \
    #                                 | //field[@name='practice_billing_id'] \
    #                                 | //field[@name='sales_partner_id']"):
    #                 node.set("readonly", "0")
    #                 modifiers = json.loads(node.get("modifiers"))
    #                 modifiers['readonly'] = False
    #                 node.set("modifiers", json.dumps(modifiers))
    #         res['arch'] = etree.tostring(doc)
    #     return res

    # overriding this method to add the birthdate in display name
    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        partner = self
        name = partner.name or ''
        # custom code
        # commit_assetsbundle this is put for the report printing (so not print the birthdate)
        if partner.patient_birthday and 'commit_assetsbundle' not in self._context:
            name += ' [' + partner.patient_birthday.strftime("%m/%d/%Y") + ']'
        # end custom code

        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
            # added this condition 'commit_assetsbundle' not in self._context 
            # to not print parent name in address
            if not partner.is_company and 'commit_assetsbundle' not in self._context:
                name = self._get_contact_name(partner, name)
        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')
        if self._context.get('partner_show_db_id'):
            name = "%s (%s)" % (name, partner.id)
        if self._context.get('address_inline'):
            splitted_names = name.split("\n")
            name = ", ".join([n for n in splitted_names if n.strip()])
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)
        return name

    '''
    # commented due to buggy code
    def name_get(self):
        """
        Append birthdate to the partner name.
        """
        res_data = super(ResPartner, self).name_get()
        final_data = []
        for res in res_data:
            partner = self.browse(res[0])
            partner_string = partner.name
            if partner.patient_birthday:
                partner_string += ' [' + partner.patient_birthday.strftime("%m/%d/%Y") + ']'
            final_data.append((res[0], partner_string))
        return final_data
    '''

# ResPartner()
