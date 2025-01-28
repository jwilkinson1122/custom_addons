# -*- coding: utf-8 -*-

import logging
import json
from lxml import etree

from odoo import api, fields, models, _, exceptions, tools
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fax_number = fields.Char(string="Fax")
    # ref = fields.Char(string="Ref", index=True)
    legacy_customer_code = fields.Char("Legacy ID", readonly=True)
    parent_relation_label = fields.Char(related='partner_type_id.parent_relation_label', readonly=True)
    companies_label = fields.Char(related='partner_type_id.companies_label', readonly=True)
    is_account = fields.Boolean(
        string='Account', default=True,
        help="Check this box if this is a Customer Account.")
    is_affiliate = fields.Boolean(
        string='Affiliate',
        help="Check this box if this is an Company Affiliate.")
    is_contact = fields.Boolean(
        string='Contact',
        help="Check this box if this is a Company Contact.")
    is_patient = fields.Boolean(
        string='Patient',
        help="Check this box if this is a Patient.")
    commercial_partner = fields.Boolean(
        string="Trading Company",
        help="Set this to True if this partner should be treated as its own trading company, "
        "even if it has a parent company.",
    )

    @api.depends("commercial_partner", "parent_id")
    def _compute_commercial_partner(self):
        """
        Override the computation of commercial_partner_id to allow a contact to be its own trading company.
        """
        for partner in self:
            if partner.commercial_partner or not partner.parent_id:
                partner.commercial_partner_id = partner
            else:
                partner.commercial_partner_id = partner.parent_id.commercial_partner_id

    parent_id = fields.Many2one(ondelete='restrict')
    partner_type_id = fields.Many2one('res.partner.type', 'Partner Type')
    partner_type_code = fields.Char(
        string="Partner Type Code",
        related="partner_type_id.code",  
        store=True,
        readonly=True,
    )

    type = fields.Selection(default=False)

    partner_company_type = fields.Many2one(
        string="Company Type",
        comodel_name="partner.company.type",
        help="Select the type of company this belongs to.",
    )

    company_address_type = fields.Selection(
        selection=[
            ("invoice", "Invoice Address"),
            ("delivery", "Delivery Address"),
            ("other", "Other Address"),
        ],
        string="Company Address Type",
        compute="_compute_company_address_type",
        inverse="_inverse_company_address_type",
        store=True,
    )

    contact_address_type = fields.Selection(
        selection=[
            ("contact", "Contact Address"),
            ("patient", "Patient Address"),
        ],
        compute="_compute_contact_address_type",
        string="Contact Address Type",
        default="contact",
        required=False,
    )

    @api.depends("type")
    def _compute_company_address_type(self):
        """
        Compute the company_address_type based on the type field, filtering allowed options.
        """
        for record in self:
            if record.type in dict(self._fields["company_address_type"].selection):
                record.company_address_type = record.type
            else:
                record.company_address_type = False

    def _inverse_company_address_type(self):
        """
        Set the type field based on company_address_type when it changes.
        """
        for record in self:
            if record.company_address_type:
                record.type = record.company_address_type

    @api.depends("type", "partner_type_code")
    def _compute_contact_address_type(self):
        """
        Compute the contact_address_type based on the type field and partner_type_code.
        Default to "contact" or "patient" based on partner_type_code.
        """
        for record in self:
            if record.partner_type_code == "PATIENT":
                record.contact_address_type = "patient"
            elif record.type in dict(self._fields["contact_address_type"].selection):
                record.contact_address_type = record.type
            else:
                record.contact_address_type = "contact"  # Fallback default


    can_have_parent = fields.Boolean(compute='_compute_partner_type_infos')
    parent_is_required = fields.Boolean(compute='_compute_partner_type_infos')
    parent_type_ids = fields.Many2many(
        'res.partner.type', 
        string='Company types authorized for parent', 
        compute='_compute_parent_types'
    )
    
    # Affiliates
    affiliate_ids = fields.One2many(
        'res.partner', 
        'parent_id', 
        string='Affiliates',
        compute='_compute_affiliate_ids',
        domain=[('active', '=', True), ('is_company', '=', True)],
        help="Directly associated affiliates (children)."
    )
    affiliates_count = fields.Integer('Number of Affiliates', store=True, recursive=True, compute='_compute_affiliates_count', compute_sudo=True)
    
    @api.depends('child_ids')
    def _compute_affiliate_ids(self):
        """
        Compute the direct affiliates for each partner.
        """
        for partner in self:
            partner.affiliate_ids = partner.child_ids.filtered(lambda c: c.is_company)

    @api.depends('affiliate_ids')
    def _compute_affiliates_count(self):
        """
        Compute the number of direct affiliates.
        """
        for partner in self:
            partner.affiliates_count = len(partner.affiliate_ids)

    @api.constrains('parent_id', 'partner_type_code')
    def _check_parent_id_for_affiliates(self):
        for partner in self:
            if partner.partner_type_code == 'AFFILIATE' and not partner.parent_id:
                raise ValidationError(_("Affiliates must have a parent partner defined."))

    @api.constrains('parent_id')
    def _check_no_circular_reference(self):
        """
        Ensure no circular references exist in parent-child relationships.
        """
        for partner in self:
            # Check for direct self-reference
            if partner.parent_id and partner.parent_id.id == partner.id:
                raise ValidationError(_("A partner cannot be its own parent."))

            # Check for hierarchical circular references
            visited = set()
            current = partner.parent_id
            while current:
                if current.id in visited:
                    raise ValidationError(_("Circular reference detected in the hierarchy."))
                visited.add(current.id)
                current = current.parent_id

    # Sub Affiliates
    sub_affiliate_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Affiliates",
        compute="_compute_sub_affiliate_ids",
        # store=False,
        help="Indirectly associated affiliates (grandchildren)."
    )

    def _get_all_sub_affiliates(self):
        """
        Recursively fetch all sub-affiliates for the current partner, excluding direct affiliates.
        """
        sub_affiliates = self.env["res.partner"]
        for affiliate in self.affiliate_ids:
            sub_affiliates |= affiliate.affiliate_ids  # Direct affiliates of the current affiliate
            sub_affiliates |= affiliate._get_all_sub_affiliates()  # Recursively fetch deeper levels
        return sub_affiliates

    @api.depends("affiliate_ids", "affiliate_ids.affiliate_ids")
    def _compute_sub_affiliate_ids(self):
        """
        Compute sub-affiliates for each partner.
        """
        for partner in self:
            all_sub_affiliates = partner._get_all_sub_affiliates()
            partner.sub_affiliate_ids = all_sub_affiliates - partner.affiliate_ids  # Exclude direct affiliates

    # Contacts
    contact_ids = fields.One2many(
        'res.partner', 'parent_id',
        string='Contacts',
        compute='_compute_contact_ids',
        help="Directly associated contacts (children)."
    )
    contacts_count = fields.Integer('Number of Contacts', compute='_compute_contacts_count')
    contacts_label = fields.Char(related='partner_type_id.contacts_label', readonly=True)
    
    @api.depends('child_ids')
    def _compute_contact_ids(self):
        for partner in self:
            partner.contact_ids = partner.child_ids.filtered(
                lambda c: not c.is_company and c.partner_type_id.code != 'CONTACT'
            )

    # Sub Contacts
    sub_contact_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Contacts",
        compute="_compute_sub_contact_ids",
        # store=False,
        help="Indirectly associated contacts (grandchildren)."
    )

    def _get_all_sub_contacts(self):
        """
        Recursively fetch all sub-contacts for the current company,
        excluding direct child contacts and patients.
        """
        sub_contacts = self.env["res.partner"]
        if self.is_company:
            for child in self.child_ids:
                if not child.is_company and child.partner_type_id.code != 'PATIENT':  # Exclude patients and include only non-companies
                    _logger.debug("Adding direct child contact: %s (ID: %s)", child.name, child.id)
                    sub_contacts |= child  # Include the direct child contact
                # Recursively fetch all contacts for the child, including deeper levels
                sub_contacts |= child._get_all_sub_contacts()
        return sub_contacts
    
    @api.depends("child_ids", "child_ids.child_ids")
    def _compute_sub_contact_ids(self):
        """
        Compute sub-contacts for the current company, excluding patients.
        """
        for partner in self:
            if partner.is_company:  # Ensure we compute for companies only
                _logger.debug("Computing sub-contacts for company: %s (ID: %s)", partner.name, partner.id)
                all_sub_contacts = partner._get_all_sub_contacts()
                # Exclude direct child contacts from the results
                final_sub_contacts = all_sub_contacts - partner.child_ids.filtered(
                    lambda c: not c.is_company and c.partner_type_id.code != 'PATIENT'
                )
                _logger.debug("Final sub-contacts for company %s (ID: %s): %s", partner.name, partner.id, final_sub_contacts)
                partner.sub_contact_ids = final_sub_contacts
            else:
                partner.sub_contact_ids = self.env["res.partner"]  # Empty for non-companies

    responsible_contact_id = fields.Many2one(
        'res.partner',
        string="Responsible Contact",
        domain="[('parent_id', '=', parent_id), ('is_company', '=', False)]",
        help="The contact responsible for the patient. Only contacts from the selected company/affiliate are available.",
    )

    def apply_contact_logic(self):
        """
        Automatically assign the first available contact from the parent company/affiliate
        to the responsible_contact_id field.
        """
        if self.parent_id:
            contacts = self.env["res.partner"].search([
                ("parent_id", "=", self.parent_id.id),
                ("is_company", "=", False)
            ])
            if contacts:
                self.responsible_contact_id = contacts[0]
                _logger.debug(
                    f"Responsible contact set to {contacts[0].name} (ID: {contacts[0].id}) for partner {self.name} (ID: {self.id})."
                )
            else:
                _logger.debug(f"No contacts found for parent_id {self.parent_id.id}.")

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        """
        Update the responsible_contact_id and dynamically adjust its domain 
        based on the selected parent_id.
        """
        _logger.debug(f"Onchange triggered for parent_id: {self.parent_id and self.parent_id.id or 'None'}")
        
        self.apply_contact_logic()
        
        domain = [("is_company", "=", False)]
        if self.parent_id:
            domain.append(("parent_id", "=", self.parent_id.id))
            _logger.debug(f"Domain updated to restrict to contacts of parent_id {self.parent_id.id}.")
        else:
            _logger.debug("Domain reset to allow any non-company contacts.")
        
        return {"domain": {"responsible_contact_id": domain}}

    # Patients
    patient_ids = fields.One2many(
        'res.partner', 'parent_id', string='Patients',
        domain=[('partner_type_id.code', '=', 'PATIENT')],
        help="Directly associated patients."
    )
    patients_count = fields.Integer('Number of Patients', compute='_compute_patients_count')

    # Link to orthotic.prescription model
    patient_prescriptions = fields.One2many(
        'orthotic.prescription', 'partner_id', string="Prescriptions"
    )

    @api.depends('partner_type_id')
    def _compute_patient(self):
        """Determine if the partner is a patient based on the type code."""
        for partner in self:
            partner.patient = partner.partner_type_id.code == 'PATIENT'

    patient = fields.Boolean(
        string="Is a Patient", compute="_compute_patient", store=True
    )

    # Sub-Patients
    sub_patient_ids = fields.One2many(
        comodel_name="res.partner",
        string="Sub-Patients",
        compute="_compute_sub_patient_ids",
        store=False,
        help="All sub-patients recursively associated with this company."
    )

    def _get_all_sub_patients(self):
        """
        Recursively fetch all sub-patients for the current company,
        excluding direct child patients.
        """
        sub_patients = self.env["res.partner"]
        if self.is_company:
            for child in self.child_ids:
                if child.partner_type_id.code == 'PATIENT':  # Include only patients
                    _logger.debug("Adding direct child patient: %s (ID: %s)", child.name, child.id)
                    sub_patients |= child  # Include the direct child patient
                # Recursively fetch all sub-patients for the child, including deeper levels
                sub_patients |= child._get_all_sub_patients()
        return sub_patients

    @api.depends("child_ids", "child_ids.child_ids")
    def _compute_sub_patient_ids(self):
        """
        Compute sub-patients for the current company.
        """
        for partner in self:
            if partner.is_company:  # Ensure we compute for companies only
                _logger.debug("Computing sub-patients for company: %s (ID: %s)", partner.name, partner.id)
                all_sub_patients = partner._get_all_sub_patients()
                # Exclude direct child patients from the results
                partner.sub_patient_ids = all_sub_patients - partner.patient_ids
                _logger.debug("Final sub-patients for company %s (ID: %s): %s", partner.name, partner.id, partner.sub_patient_ids)
            else:
                partner.sub_patient_ids = self.env["res.partner"]  # Empty for non-companies

    @api.depends('patient_ids')
    def _compute_patients_count(self):
        """
        Compute the number of direct patients for each partner.
        """
        for partner in self:
            partner.patients_count = len(partner.patient_ids)

    @api.depends('partner_type_id')
    def _compute_parent_types(self):
        for partner in self:
            if partner.partner_type_id:
                partner.parent_type_ids = partner.partner_type_id.parent_type_ids
            else:
                partner.parent_type_ids = self.env['res.partner.type'].browse()

    @api.depends('partner_type_id')
    def _compute_partner_type_infos(self):
        """Compute parent-related fields based on partner type."""
        for partner in self:
            partner.can_have_parent = True
            partner.parent_is_required = False
            if partner.partner_type_id and partner.partner_type_id.can_have_parent:
                partner.can_have_parent = True
                partner.parent_is_required = partner.partner_type_id.parent_is_required

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        _logger.debug(f"Default values before setting contact_address_type: {res}")
        
        # Set `contact_address_type` based on the context
        default_type = self._context.get("default_contact_address_type")
        if default_type:
            res["contact_address_type"] = default_type
            _logger.debug(f"Set default contact_address_type to: {default_type}")
        elif self._context.get("default_partner_type_code") == "PATIENT":
            res["contact_address_type"] = "patient"
            _logger.debug("Set default contact_address_type to 'patient' based on context.")
        else:
            res["contact_address_type"] = "contact"
            _logger.debug("Set default contact_address_type to 'contact' as fallback.")

        return res

    @api.onchange('company_type')
    def _onchange_company_type(self):
        type_mapping = {
            'company': 'ACCOUNT' if self.is_account else 'AFFILIATE',
            'person': 'PATIENT' if self.is_patient else 'CONTACT',
        }
        code = type_mapping.get(self.company_type, 'CONTACT')
        self.partner_type_id = self.env['res.partner.type'].search([('code', '=', code)], limit=1)

    @api.onchange('partner_type_id')
    def _onchange_partner_type(self):
        """Handle changes in partner type to update parent-related fields."""
        self.update(self._get_inherit_values(self.partner_type_id))
        if self.partner_type_id and self.partner_type_id.can_have_parent:
            self.can_have_parent = True
        else:
            self.can_have_parent = False

    @api.onchange("partner_type_code")
    def _onchange_partner_type_code(self):
        if self.partner_type_code:
            partner_type = self.env["res.partner.type"].search([("code", "=", self.partner_type_code)], limit=1)
            if partner_type and self.partner_type_id != partner_type.id:
                self.partner_type_id = partner_type
                _logger.debug(f"Set partner_type_id in onchange method to: {partner_type.id}")

    def _get_inherit_values(self, partner_type, not_null=False):
        """
        Fetch inherited field values based on the partner type.
        """
        if not partner_type:
            return {}

        inherit_fields = getattr(partner_type, f"_{partner_type.company_type}_inherit_fields", [])
        inherit_values = partner_type.read(inherit_fields)[0]

        if "id" in inherit_values:
            del inherit_values["id"]

        if not_null:
            # Remove fields with null values if not_null is True
            inherit_values = {k: v for k, v in inherit_values.items() if v}

        return inherit_values

    def _update_children(self, vals):
        """
        Update child records with inherited values.
        """
        for partner in self:
            if partner.child_ids and partner.partner_type_id.field_ids:
                children_vals = {
                    key: value
                    for key, value in vals.items()
                    if key in partner.partner_type_id.field_ids.mapped("name")
                }
                if children_vals:
                    partner.child_ids.write(children_vals)
            if 'ref' in partner.partner_type_id.field_ids.mapped("name"):
                _logger.debug(f"Updating children with ref: {vals.get('ref')}")

    @api.model
    def create(self, vals):
        if not vals.get("partner_type_id") and vals.get("partner_type_code"):
            _logger.debug(f"Partner type before change: {self.partner_type_id} (Code: {self.partner_type_code})")

            partner_type = self.env["res.partner.type"].search([("code", "=", vals["partner_type_code"])], limit=1)
            if partner_type:
                vals["partner_type_id"] = partner_type.id
                _logger.debug(f"Set partner_type_id in create method to: {partner_type.id}")
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        """
        Overridden write method to handle reference generation, partner type inheritance, 
        and updating children records.
        """
        partners_by_type = {}

        # Handle partner type inheritance and grouping
        if vals.get('partner_type_id'):
            partner_type = self.env['res.partner.type'].browse(vals['partner_type_id'])
            partners_by_type[partner_type] = self
        else:
            for partner in self:
                partners_by_type.setdefault(partner.partner_type_id, self.browse())
                partners_by_type[partner.partner_type_id] |= partner

        for partner_type, partners in partners_by_type.items():
            if partner_type and list(vals.keys()) != ['is_company']:  # Avoid infinite loop
                vals.update(self._get_inherit_values(partner_type, not_null=True))

            _logger.debug(f"Updating partner with vals: {vals}")

            # Write the updated values
            super(ResPartner, partners).write(vals)

        # Update children with inherited values
        self._update_children(vals)
        return True

    @api.model
    def _commercial_fields(self):
        """
        Make the partner reference a field that is propagated
        to the partner's contacts
        """
        return super()._commercial_fields() + ["ref"]

    @api.constrains("legacy_customer_code")
    def _check_unique_legacy_code(self):
        for record in self:
            if record.legacy_customer_code:
                duplicate = self.search(
                    [
                        ("legacy_customer_code", "=", record.legacy_customer_code),
                        ("id", "!=", record.id),
                    ],
                    limit=1,
                )
                if duplicate:
                    raise ValidationError(
                        _(
                            "Legacy Customer Code must be unique. Found duplicate for: %s"
                        )
                        % record.legacy_customer_code
                    )

    def view_affiliates(self):
        return {
            'name': _('Affiliates'),
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'tree,form',
            'view_id': False,
            'domain': [
                ('parent_id', 'in', self.ids),
                ('is_company', '=', True)
            ],
            'target': 'current',
        }

    def _update_fields_view_get_result(self, result, view_type='form'):
        if view_type == 'form' and not self._context.get(
            'display_original_view'):
            # In order to inherit all views based on the field order_line
            doc = etree.XML(result['arch'])
            for node in doc.xpath("//field[@name='child_ids']"):
                node.set('name', 'contact_ids')
                node.set('modifiers', json.dumps(
                    {'default_customer': False, 'default_is_affiliate': False}))
                result['fields']['contact_ids'] = result['fields']['child_ids']
                result['fields']['contact_ids'].update(
                    self.fields_get(['contact_ids'])['contact_ids'])
            result['arch'] = etree.tostring(doc)
        return result

    def get_view(self, view_id=None, view_type='form', **options):
        result = super(ResPartner, self).get_view(view_id, view_type, **options)
        node = etree.fromstring(result['arch'])
        view_fields = set(el.get('name') for el in node.xpath('.//field[not(ancestor::field)]'))
        result['fields'] = self.fields_get(view_fields)
        return self._update_fields_view_get_result(result, view_type)

    @api.model
    def _format_args(self, args):
        for cond in (args or []):
            if len(cond) == 3 and cond[2] and isinstance(cond[2], list) and \
                isinstance(cond[2][0], list):
                for index, item in enumerate(cond[2]):
                    if item[0] == 1:
                        cond[2][index] = item[1]
                    elif item[0] == 6:
                        cond[2] = item[2]
                        break

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        self._format_args(args)
        return super(ResPartner, self).name_search(name, args, operator, limit)

    def _search(self, args, offset=0, limit=None, order=None, count=False):
        self._format_args(args)
        _logger.debug("Search args: %s", args)
        if count:
            return super(ResPartner, self)._search(args, offset=offset, limit=limit, order=order, count=True)
        return super(ResPartner, self)._search(args, offset=offset, limit=limit, order=order)

    # Sales Orders
    sale_order_ids = fields.One2many(
        "sale.order",
        "partner_id",
        string="Sale Orders",
    )

    current_sale_order_ids = fields.One2many(
        "sale.order",
        compute="_compute_current_sale_order_ids",
        string="Current Orders",
        store=False,
    )

    historic_sale_order_ids = fields.One2many(
        "sale.order",
        compute="_compute_historic_sale_order_ids",
        string="Historic Orders",
        store=False,
    )

    reorder_count = fields.Integer(
        compute="_compute_reorder_order_count",
        string="Reorder",
    )

    def _compute_current_sale_order_ids(self):
        """
        Compute method to populate the 'current_sale_order_ids' field.
        Includes all sales orders that are not done or canceled.
        """
        for partner in self:
            partner.current_sale_order_ids = partner.sale_order_ids.filtered(
                lambda order: order.state not in ("done", "cancel")
            )

    def _compute_historic_sale_order_ids(self):
        """
        Compute method to populate the 'historic_sale_order_ids' field.
        Includes all sales orders that are done or canceled and can be reordered.
        """
        for partner in self:
            partner.historic_sale_order_ids = partner.sale_order_ids.filtered(
                lambda order: order.state in ("done", "cancel") and order.is_reorder
            )

    def _compute_reorder_order_count(self):
        """
        Compute the count of reorderable historic sale orders for the partner.
        """
        for partner in self:
            partner.reorder_count = len(partner.historic_sale_order_ids)

    def open_sale_from_view_action(self):
        """
        Open the sale orders action filtered by reorder sales for the partner.
        """
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action["domain"] = [
            ("partner_id", "=", self.id),
            ("state", "=", "sale"),
            ("is_reorder", "=", True),
        ]
        return action