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
    is_organization = fields.Boolean(string="Organization", tracking=True)
    is_practice = fields.Boolean(string="Practice", tracking=True)
    is_practitioner = fields.Boolean(string="Practitioner", tracking=True)
    is_personnel = fields.Boolean(string="Personnel", tracking=True)
    is_sales_partner = fields.Boolean(string="Sales Partner", tracking=True)
    # pod_organization = fields.Boolean(string="Organization", tracking=True)
    # pod_practice = fields.Boolean(string="Practice", tracking=True)
    # pod_practitioner = fields.Boolean(string="Practitioner", tracking=True)
    # pod_personnel = fields.Boolean(string="Personnel", tracking=True)
    # pod_sales_partner = fields.Boolean(string="Sales Partner", tracking=True)

    # pod_contact_type_id = fields.Many2one("contact.type",string="Contact Type", tracking=True)
    pod_uuid = fields.Char(string="Contact UUID", index=True)
    pod_medical_record_number = fields.Char(string="Medical Record Number", tracking=True)
    pod_program_group = fields.Char(string="Program Group", tracking=True)
    # pod_program_ids = fields.Many2many("pod.program", "res_partner_pod_program_rel", "partner_id", "pod_program_id", string="Programs", tracking=True)
    # pod_status_ids = fields.Many2one("pod.status", string="Status", tracking=True)
    pod_patient_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender", tracking=True)
    pod_patient_birthday = fields.Date('Date of Birth', tracking=True)
    pod_patient_birthday_str = fields.Char(string='Birthday string', compute='compute_pod_patient_birthday_str',
                                           store=True, help='Technical Date of Birth in string format for search')
    pod_patient_url = fields.Char(string="Patient URL", tracking=True)
    pod_fax = fields.Char(string="Fax", tracking=True)
 
    
    
    # Types of contacts
    pod_practice_id = fields.Many2one("res.partner", string="Practice", tracking=True)
    pod_medical_id = fields.Many2one("res.partner", string="Primary Practitioner", tracking=True)
    pod_medical_billing_id = fields.Many2one("res.partner", string="Billing Practitioner", tracking=True)
    pod_medical_asst_id = fields.Many2one("res.partner", string="Assitant", tracking=True)
    pod_organization_id = fields.Many2one("res.partner", string="Organization", tracking=True)
    pod_sales_partner_id = fields.Many2one("res.partner", string="Sales Partner", tracking=True)
    pod_warehouse_id = fields.Many2one("stock.warehouse", string="Default Warehouse", tracking=True)

    # Insurance Fields
    # primary_subscriber_id = fields.Char(string="Primary Subscriber ID")
    # primary_carrier = fields.Char(string="Primary Carrier")
    # primary_group_name = fields.Char(string="Primary Group Name")
    # primary_group_number = fields.Char(string="Primary Group Number")
    # primary_relationship = fields.Char(string="Primary Relationship")
    # primary_start_date = fields.Datetime(string="Primary Start Date")
    # primary_subscriber_name = fields.Char(string="Primary Subscriber Name")
    # primary_subscriber_birthdate = fields.Date(string="Primary Subscriber Birthdate")

    # secondary_subscriber_id = fields.Char(string="Secondary Subscriber ID")
    # secondary_carrier = fields.Char(string="Secondary Carrier")
    # secondary_group_name = fields.Char(string="Secondary Group Name")
    # secondary_group_number = fields.Char(string="Secondary Group Number")
    # secondary_relationship = fields.Char(string="Secondary Relationship")
    # secondary_start_date = fields.Datetime(string="Secondary Start Date")
    # secondary_subscriber_name = fields.Char(string="Secondary Subscriber Name")
    # secondary_subscriber_birthdate = fields.Date(string="Secondary Subscriber Birthdate")
    pod_order_uuid = fields.Char(string="Pod Order UUID", index=True)

    _sql_constraints = [
        ("pod_uuid_unique", "unique(pod_uuid)", 'Contact UUID Must be Unique!')
    ]

    @api.depends('pod_patient_birthday')
    def compute_pod_patient_birthday_str(self):
        """
        Compute method to set birthdate as string in new field.
        """
        for partner in self:
            partner.pod_patient_birthday_str = partner.pod_patient_birthday and partner.pod_patient_birthday.strftime("%m/%d/%Y") or ""

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
    #             for node in doc.xpath("//field[@name='pod_practice_id'] \
    #                                 | //field[@name='pod_medical_id'] \
    #                                 | //field[@name='pod_medical_asst_id'] \
    #                                 | //field[@name='pod_organization_id'] \
    #                                 | //field[@name='pod_medical_billing_id'] \
    #                                 | //field[@name='pod_sales_partner_id']"):
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
        if partner.pod_patient_birthday and 'commit_assetsbundle' not in self._context:
            name += ' [' + partner.pod_patient_birthday.strftime("%m/%d/%Y") + ']'
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
            if partner.pod_patient_birthday:
                partner_string += ' [' + partner.pod_patient_birthday.strftime("%m/%d/%Y") + ']'
            final_data.append((res[0], partner_string))
        return final_data
    '''

# ResPartner()
