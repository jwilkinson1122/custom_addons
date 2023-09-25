import base64
import logging
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Fields
    parent_id_is_company = fields.Boolean(
        string='Parent Is a Practice',
        related='parent_id.is_company',
        readonly=True,
        store=False,
    )
    affiliate_ids = fields.One2many(
        "res.partner",
        compute="_compute_affiliates",
        string="Affiliates",
        readonly=True,
    )
    
    type = fields.Many2many('res.partner.type', string="Address Types")
    child_ids = fields.One2many(domain=[("active", "=", True), ("is_company", "=", False)])
    child_count = fields.Integer(string='Contact Count', compute='_compute_affiliate_and_child_counts')
    affiliate_count = fields.Integer(string='Affiliate Count', compute='_compute_affiliate_and_child_counts')
    affiliate_text = fields.Char(compute="_compute_affiliate_text")
    child_text = fields.Char(compute="_compute_child_text")

    # Compute Methods
    @api.depends('parent_id', 'is_company', 'active')
    def _compute_affiliates(self):
        for record in self:
            # Check if the record has a proper ID
            if not isinstance(record.id, models.NewId):
                all_affiliates = self.env['res.partner'].search([
                    ('id', 'child_of', record.id), 
                    ("is_company", "=", True), 
                    ("active", "=", True)
                ])
                record.affiliate_ids = all_affiliates - record
            else:
                record.affiliate_ids = self.env['res.partner']  # Empty recordset


    @api.depends('child_ids', 'child_ids.is_company')
    def _compute_affiliate_and_child_counts(self):
        for record in self:
            if not isinstance(record.id, models.NewId):
                all_partners = self.env['res.partner'].search([('parent_id', 'child_of', record.id)])
                all_partners -= record

                affiliates = all_partners.filtered(lambda p: p.is_company)
                record.affiliate_count = len(affiliates)

                contacts = all_partners.filtered(lambda p: not p.is_company)
                record.child_count = len(contacts)
            else:
                record.affiliate_count = 0
                record.child_count = 0

    @api.depends('affiliate_count')
    def _compute_affiliate_text(self):
        for record in self:
            if not record.affiliate_count:
                record.affiliate_text = False
            elif record.affiliate_count == 1:
                record.affiliate_text = _("(1 Affiliate)")
            else:
                record.affiliate_text = _("(%s Affiliates)" % record.affiliate_count)

    @api.depends('child_count')
    def _compute_child_text(self):
        for record in self:
            if not record.child_count:
                record.child_text = False
            elif record.child_count == 1:
                record.child_text = _("(1 Contact)")
            else:
                record.child_text = _("(%s Contacts)" % record.child_count)

    # Onchange Methods
    @api.onchange('company_type')
    def _onchange_company_type(self):
        for partner in self:
            if partner.company_type == 'person':
                contact_type = self.env['res.partner.type'].search([('name', '=', 'contact')], limit=1)
                if contact_type:
                    partner.type = [(6, 0, [contact_type.id])]
                partner.is_company = False
            elif partner.company_type == 'company':
                partner.is_company = True
