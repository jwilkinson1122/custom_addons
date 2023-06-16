# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.exceptions import AccessError

import logging
_logger = logging.getLogger(__name__)

INVOICE = "invoice"

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    code = fields.Char("Code", required=True, help="Partner code")
    info_ids = fields.One2many('res.partner.info', 'partner_id', string="More Info")
    active_id = fields.Boolean(string="Active", default=True, tracking=True)
    name = fields.Char(index=True)
    partner_id = fields.Many2one('res.partner', "Contact", copy=False)
    clinic_id = fields.Many2one("podiatry.podiatry",string="Clinic")
    clinic_ids = fields.One2many('podiatry.podiatry', 'clinic_address_id', string='Clinics')
    # clinic_ids = fields.One2many('podiatry.podiatry', 'clinic_id', string='Related Clinic')
    other_clinic_ids = fields.One2many("res.partner", "clinic_id", string="Others Clinics")
    is_clinic = fields.Boolean(compute = '_calc_clinic', compute_sudo = True, store = True, string='Is Clinic', search='_search_is_clinic')
    clinics_count = fields.Integer(string="Clinics Count", compute='_compute_clinics_count')
    use_parent_invoice_address = fields.Boolean()
    
 
    @api.depends('clinic_ids')
    def _calc_clinic(self):
        for record in self:
            record.is_clinic = bool(record.clinic_ids)
            
    # Clinics
    @api.depends('clinic_ids')
    def _compute_clinics_count(self):
        for partner in self:
            partner.clinics_count = partner.clinic_id
        return

    def _search_is_clinic(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('clinic_id', search_operator, False)]
    
    
    def name_get(self):
        """ Override to allow a clinic to see its address in his profile.
            This avoids to relax access rules on `res.parter` and to add an `ir.rule`.
            (advantage in both security and performance).
            Use a try/except instead of systematically checking to minimize the impact on performance.
            """
        try:
            return super(ResPartner, self).name_get()
        except AccessError as e:
            if len(self) == 1 and self in self.env.user.clinic_ids.mapped('clinic_address_id'):
                return super(ResPartner, self.sudo()).name_get()
            raise e
        
        
    def _compute_clinics_count(self):
        for partner in self:
            partner.clinics_count = len(partner.clinic_ids)


    def _search_is_clinic(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('clinic_id', search_operator, False)]

    clinic_type = fields.Selection(
        [
            ("standalone", "Standalone Clinic"),
            ("attached", "Attached to existing Clinic"),
        ],
        compute="_compute_clinic_type",
        store=True,
        index=True,
        default="standalone",
    )

    @api.depends("clinic_id")
    def _compute_clinic_type(self):
        for rec in self:
            rec.clinic_type = "attached" if rec.clinic_id else "standalone"

    def _base_clinic_check_context(self, mode):
        """Remove "search_show_all_clinics" for non-search mode.
        Keeping it in context can result in unexpected behaviour (ex: reading
        one2many might return wrong result - i.e with "attached clinic"
        removed even if it"s directly linked to a company).
        Actually, is easier to override a dictionary value to indicate it
        should be ignored...
        """
        if mode != "search" and "search_show_all_clinics" in self.env.context:
            result = self.with_context(
                search_show_all_clinics={"is_set": False})
        else:
            result = self
        return result
    
    @api.model
    def create(self, vals):
        """When creating, use a modified self to alter the context (see
        comment in _basepractitioner_check_context).  Also, we need to ensure
        that the name on an attached practitioner is the same as the name on the
        practitioner it is attached to."""
        modified_self = self._base_clinic_check_context("create")
        if not vals.get("name") and vals.get("clinic_id"):
            vals["name"] = modified_self.browse(vals["clinic_id"]).name
        return super(ResPartner, modified_self).create(vals)

    def read(self, fields=None, load="_classic_read"):
        modified_self = self._base_clinic_check_context("read")
        return super(ResPartner, modified_self).read(fields=fields, load=load)

    def write(self, vals):
        modified_self = self._base_clinic_check_context("write")
        return super(ResPartner, modified_self).write(vals)
    
    def unlink(self):
        modified_self = self._base_clinic_check_context("unlink")
        return super(ResPartner, modified_self).unlink()

    def _compute_commercial_partner(self):
        """Returns the partner that is considered the commercial
        entity of this partner. The commercial entity holds the master data
        for all commercial fields (see :py:meth:`~_commercial_fields`)"""
        result = super(ResPartner, self)._compute_commercial_partner()
        for partner in self:
            if partner.clinic_type == "attached" and not partner.parent_id:
                partner.commercial_partner_id = partner.clinic_id
        return result

    def _clinic_fields(self):
        """Returns the list of clinic fields that are synced from the parent
        when a partner is attached to him."""
        return ["name", "title"]

    def _clinic_sync_from_parent(self):
        """Handle sync of clinic fields when a new parent clinic entity
        is set, as if they were related fields
        """
        self.ensure_one()
        if self.clinic_id:
            clinic_fields = self._clinic_fields()
            sync_vals = self.clinic_id._update_fields_values(
                clinic_fields)
            self.write(sync_vals)

    def update_clinic(self, vals):
        if self.env.context.get("__update_clinic_lock"):
            return
        clinic_fields = self._clinic_fields()
        clinic_vals = {field: vals[field]
                             for field in clinic_fields if field in vals}
        if clinic_vals:
            self.with_context(__update_clinic_lock=True).write(
                clinic_vals)

    def _fields_sync(self, update_values):
        """Sync commercial fields and address fields from company and to
        children, clinic fields from clinic and to attached clinic
        after create/update, just as if those were all modeled as
        fields.related to the parent
        """
        self.ensure_one()
        super(ResPartner, self)._fields_sync(update_values)
        clinic_fields = self._clinic_fields()
        # 1. From UPSTREAM: sync from parent clinic
        if update_values.get("clinic_id"):
            self._clinic_sync_from_parent()
        # 2. To DOWNSTREAM: sync clinic fields to parent or related
        elif any(field in clinic_fields for field in update_values):
            update_ids = self.other_clinic_ids.filtered(
                lambda p: not p.is_clinic)
            if self.clinic_id:
                update_ids |= self.clinic_id
            update_ids.update_clinic(update_values)

    @api.onchange("clinic_id")
    def _onchange_clinic_id(self):
        if self.clinic_id:
            self.name = self.clinic_id.name

    @api.onchange("clinic_type")
    def _onchange_clinic_type(self):
        if self.clinic_type == "standalone":
            self.clinic_id = False
            
    def action_open_clinics(self):
        self.ensure_one()
        return {
            'name': _('Related Clinics'),
            'type': 'ir.actions.act_window',
            'res_model': 'podiatry.podiatry',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', self.clinic_ids.ids)],
        }
        

class ResPartnerInfo(models.Model):
    _name = "res.partner.info"

    name = fields.Char(string="Extra Info", required=True)
    info_name = fields.Char(string="Info Name")
    partner_id = fields.Many2one("res.partner", string="ResPartner Info")
