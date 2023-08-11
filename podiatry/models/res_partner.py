# -*- coding: utf-8 -*-

import logging
from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import config

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    _parent_name = 'parent_id'
    _parent_store = True
    parent_path = fields.Char(string="Parent Path", index=True)
    
    info_ids = fields.One2many(
        'res.partner.info', 'partner_id', string="More Info")
    reference = fields.Char('ID Number')
    name = fields.Char(index=True)
    
    is_practice = fields.Boolean(string="Practice", search='_search_is_practice')
    is_practitioner = fields.Boolean(string="Practitioner", search='_search_is_practitioner')
    is_patient = fields.Boolean(string="Patient", search='_search_is_patient')
    is_prescription = fields.Boolean(string="Prescription", search='_search_is_prescription')
    is_practice_parent = fields.Boolean(
        compute="_get_is_practice_parent",
        store="True",
        string='Is a Parent Practice',
        help="A parent practice is a “Company” type contact for which at least "
             "one Practice is defined and for which no related"
             " company is defined"
    )
    
    practice_id = fields.Many2one(
        "res.partner",
        string="Main Practice",
        index=True,
        ondelete='cascade',
        domain=[("is_practice", "=", True), ("practice_type", "=", "standalone")],
    )
    
    parent_id = fields.Many2one(
        comodel_name='res.partner',
        string="Practice",
        index=True,
        ondelete='cascade',
        domain="['|', ('company_id', '=', False), ('practice_id', '=', company_id)]",
    )
    
    practice_ids = fields.Many2many('res.partner', 'partner_practice_rel', 'practice_id', string='Practices')
    practitioner_ids = fields.Many2many('podiatry.practitioner', 'partner_practitioner_rel', 'practitioner_id', string='Practitioners')
    patient_ids = fields.Many2many('podiatry.patient', 'partner_patient_rel', 'patient_id', string='Patients')
    prescription_ids = fields.One2many("podiatry.prescription", 'practice_id', string="Practice Prescriptions", domain=[("active", "=", True)])

    highest_parent_id = fields.Many2one(
        "res.partner",
        compute="_get_highest_parent_id",
        store="True",
        string="Highest parent"
    )
    
    child_ids = fields.One2many(
        comodel_name='podiatry.practice',
        inverse_name='parent_id',
        string="Practices",
    )
    child_count = fields.Integer(
        string="Subpractice Count",
        compute='_compute_child_count',
    )

    @api.depends('child_ids')
    def _compute_child_count(self):
        for practice in self:
            practice.child_count = len(practice.child_ids)
        return

    
    @api.depends("company_type", "practice_ids", "parent_id")
    def _get_is_practice_parent(self):
        """compute if contact is a parent company or not"""
        for rec in self:
            is_practice_parent = False
            if rec.company_type == "company" and \
                    rec.practice_ids and not rec.parent_id:
                is_practice_parent = True
            rec.is_practice_parent = is_practice_parent

    def compute_partner_parent_ids(self, rec=False, res=[]):
        if rec.parent_id:
            res.append(rec.parent_id.id)
            self.compute_partner_parent_ids(rec=rec.parent_id, res=res)
        return res

    @api.depends("parent_id", "child_ids")
    def _get_highest_parent_id(self):
        for rec in self:
            if rec.parent_id:
                res = rec.compute_partner_parent_ids(rec=rec)
                if res:
                    rec.highest_parent_id = res[-1]

    def compute_all_top_parent_id(self):
        partner_ids = self.search([('is_practice_parent', '=', False), ('parent_id', '!=', False)])
        for partner in partner_ids:
            res = partner.compute_partner_parent_ids(rec=partner)
            if res:
                partner.highest_parent_id = res[-1]

    
    practice_count = fields.Integer(string='Practice Count', compute='_compute_practice_count')
    
    def _compute_practice_count(self):
        for record in self:
            practices = self.env['podiatry.practice'].search([
                ('practice_id', 'child_of', record.id),
            ])
            record.practice_count = len(practices)
            record.practice_ids = [(6, 0, practices.ids)]
    
    def _search_is_practice(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('practice_ids', search_operator, False)]
    
    practice_type = fields.Selection(
        [("standalone", "Standalone Practice"), ("attached", "Attached to existing Practice")],
        compute="_compute_practice_type",
        store=True,
        index=True,
        default="standalone",
    )

    @api.depends("practice_id")
    def _compute_practice_type(self):
        for rec in self:
            rec.practice_type = "attached" if rec.practice_id else "standalone"

    def _base_practice_check_context(self, mode):
        if mode != "search" and "search_show_all_practices" in self.env.context:
            result = self.with_context(
                search_show_all_practices={"is_set": False})
        else:
            result = self
        return result
    
    # def _top_parent_check_context(self, vals):
    #     super().write(vals)
    #     if 'parent_id' in vals:
    #         for record in self:
    #             record.compute_all_top_parent_id()
    #     return True
    # def open_parent(self):
    #     """Utility method used to add an "Open Parent" button in partner
    #     views"""
    #     self.ensure_one()
    #     address_form_id = self.env.ref("base.view_partner_address_form").id
    #     return {
    #         "type": "ir.actions.act_window",
    #         "res_model": "res.partner",
    #         "view_mode": "form",
    #         "views": [(address_form_id, "form")],
    #         "res_id": self.parent_id.id,
    #         "target": "new",
    #         "flags": {"form": {"action_buttons": True}},
    #     }

    @api.model
    def create(self, vals):
        """When creating, use a modified self to alter the context (see
        comment in _base_practice_check_context).  Also, we need to ensure
        that the name on an attached practice is the same as the name on the
        practice it is attached to."""
        modified_self = self._base_practice_check_context("create")
        if not vals.get("name") and vals.get("practice_id"):
            vals["name"] = modified_self.browse(vals["practice_id"]).name
        return super(Partner, modified_self).create(vals)

    def read(self, fields=None, load="_classic_read"):
        modified_self = self._base_practice_check_context("read")
        return super(Partner, modified_self).read(fields=fields, load=load)
    
    # def write(self, vals):
    #     super().write(vals)
    #     if 'parent_id' in vals:
    #         for record in self:
    #             record.compute_all_top_parent_id()
    #     return True
    
    def write(self, vals):
        modified_self = self._base_practice_check_context("write")
        result = super(Partner, modified_self).write(vals)
        if 'parent_id' in vals:
            for record in self:
                record.compute_all_top_parent_id()
        return result
        
    
    def unlink(self):
        modified_self = self._base_practice_check_context("unlink")
        return super(Partner, modified_self).unlink()

    def _compute_commercial_partner(self):
        """Returns the partner that is considered the commercial
        entity of this partner. The commercial entity holds the master data
        for all commercial fields (see :py:meth:`~_commercial_fields`)"""
        result = super(Partner, self)._compute_commercial_partner()
        for partner in self:
            if partner.practice_type == "attached" and not partner.parent_id:
                partner.commercial_partner_id = partner.practice_id
        return result

    def _practice_fields(self):
        """Returns the list of practice fields that are synced from the parent
        when a partner is attached to him."""
        return ["name", "title"]

    def _practice_sync_from_parent(self):
        """Handle sync of practice fields when a new parent practice entity
        is set, as if they were related fields
        """
        self.ensure_one()
        if self.practice_id:
            practice_fields = self._practice_fields()
            sync_vals = self.practice_id._update_fields_values(
                practice_fields)
            self.write(sync_vals)

    def update_practice(self, vals):
        if self.env.context.get("__update_practice_lock"):
            return
        practice_fields = self._practice_fields()
        practice_vals = {field: vals[field]
                             for field in practice_fields if field in vals}
        if practice_vals:
            self.with_context(__update_practice_lock=True).write(
                practice_vals)

    def _fields_sync(self, update_values):
        """Sync commercial fields and address fields from company and to
        children, practice fields from practice and to attached practice
        after create/update, just as if those were all modeled as
        fields.related to the parent
        """
        self.ensure_one()
        super(Partner, self)._fields_sync(update_values)
        practice_fields = self._practice_fields()
        # 1. From UPSTREAM: sync from parent practice
        if update_values.get("practice_id"):
            self._practice_sync_from_parent()
        # 2. To DOWNSTREAM: sync practice fields to parent or related
        elif any(field in practice_fields for field in update_values):
            update_ids = self.practice_ids.filtered(
                lambda p: not p.is_company)
            if self.practice_id:
                update_ids |= self.practice_id
            update_ids.update_practice(update_values)
            
    # @api.onchange("parent_id")
    # def _onchange_parent_id(self):
    #     if self.parent_id:
    #         self.practice_id = self.parent_id

    @api.onchange("practice_id")
    def _onchange_practice_id(self):
        if self.practice_id:
            self.name = self.practice_id.name

    @api.onchange("practice_type")
    def _onchange_practice_type(self):
        if self.practice_type == "standalone":
            self.practice_id = False
    
    # Partner - Patients
    
    patient_count = fields.Integer(string='Patient Count', compute='_compute_patient_count')
    
    def _compute_patient_count(self):
        for record in self:
            patients = self.env['podiatry.patient'].search([
                ('practice_id', 'child_of', record.id),
            ])
            record.patient_count = len(patients)
            record.patient_ids = [(6, 0, patients.ids)]

    def _search_is_patient(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('patient_ids', search_operator, False)]
    
    # Partner - Practitioners

    practitioner_count = fields.Integer(string='Practitioner Count', compute='_compute_practitioner_count')
    
    def _compute_practitioner_count(self):
        for record in self:
            practitioners = self.env['podiatry.practitioner'].search([
                ('practice_id', 'child_of', record.id),
            ])
            record.practitioner_count = len(practitioners)
            record.practitioner_ids = [(6, 0, practitioners.ids)]

    def _search_is_practitioner(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('practitioner_ids', search_operator, False)]

    # Partner - Prescriptions
    prescription_count = fields.Integer(string='Prescription Count', compute='_compute_prescription_count')
    
    def _compute_prescription_count(self):
        for record in self:
            prescriptions = self.env['podiatry.prescription'].search([
                ('practice_id', 'child_of', record.id),
            ])
            record.prescription_count = len(prescriptions)
            record.prescription_ids = [(6, 0, prescriptions.ids)]

    def _search_is_prescription(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('prescription_ids', search_operator, False)]
    
    # UI
    @api.model
    def create_partner_from_ui(self, partner, extraPartner):
        """ create or modify a partner from the point of sale ui.
            partner contains the partner's fields. """
        # image is a dataurl, get the data after the comma
        extraPartner_id = partner.pop('id', False)
        if extraPartner:
            if extraPartner.get('image_1920'):
                extraPartner['image_1920'] = extraPartner['image_1920'].split(',')[
                    1]
            if extraPartner_id:  # Modifying existing extraPartner
                custom_info = self.env['custom.partner.field'].search([])
                for i in custom_info:
                    if i.name in extraPartner.keys():
                        info_data = self.env['res.partner.info'].search(
                            [('partner_id', '=', extraPartner_id), ('name', '=', i.name)])
                        if info_data:
                            info_data.write(
                                {'info_name': extraPartner[i.name], 'partner_id': extraPartner_id})
                        else:
                            self.browse(extraPartner_id).write(
                                {'info_ids': [(0, 0, {'name': i.name, 'info_name': extraPartner[i.name]})]})
            else:
                extraPartner_id = self.create(extraPartner).id

        if partner:
            if partner.get('image_1920'):
                partner['image_1920'] = partner['image_1920'].split(',')[1]
            if extraPartner_id:  # Modifying existing partner

                self.browse(extraPartner_id).write(partner)
            else:
                extraPartner_id = self.create(partner).id
        return extraPartner_id


class CustomPartnerField(models.Model):
    _name = "custom.partner.field"

    name = fields.Char(string="Custom Partner Fields")
    config_id = fields.Many2one("pos.config", string="Pos Config")


class ResPartnerInfo(models.Model):
    _name = "res.partner.info"

    name = fields.Char(string="Extra Info", required=True)
    info_name = fields.Char(string="Info Name")
    partner_id = fields.Many2one("res.partner", string="Partner Info")
    field_id = fields.Many2one("custom.partner.field", string="Custom Filed")
