# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    reference = fields.Char('ID Number')
    name = fields.Char(index=True)
    
    info_ids = fields.One2many(
        'res.partner.info', 'partner_id', string="More Info")

    practice_id = fields.One2many(
        comodel_name='podiatry.practice',
        inverse_name='partner_id',
        string="Practice",
    )

    practice_count = fields.Integer(
        string="Practice Count", store=False,
        compute='_compute_practice_count',
    )

    @api.depends('practice_id')
    def _compute_practice_count(self):
        for partner in self:
            partner.practice_count = partner.practice_id
        return

    is_practice = fields.Boolean(
        string="Practice", store=False,
        search='_search_is_practice',
    )

    def _search_is_practice(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('practice_id', search_operator, False)]

    # patient_ids = fields.One2many(
    #     comodel_name='podiatry.patient',
    #     inverse_name='partner_id',
    #     string="Patients",
    # )

    # patient_count = fields.Integer(
    #     string="Patient Count", store=False,
    #     compute='_compute_patient_count',
    # )

    # @api.depends('patient_ids')
    # def _compute_patient_count(self):
    #     for partner in self:
    #         partner.patient_count = partner.patient_ids
    #     return

    # is_patient = fields.Boolean(
    #     string="Patient", store=False,
    #     search='_search_is_patient',
    # )

    # def _search_is_patient(self, operator, value):
    #     assert operator in ('=', '!=', '<>') and value in (
    #         True, False), 'Operation not supported'
    #     if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
    #         search_operator = '!='
    #     else:
    #         search_operator = '='
    #     return [('patient_ids', search_operator, False)]

  
    doctor_id = fields.Many2one(
        comodel_name='podiatry.doctor',
        inverse_name='partner_id',
        string="Doctor",
    )
    
    other_doctor_ids = fields.One2many(
        "res.partner",
        "doctor_id",
        string="Others Positions",
    )

    doctor_count = fields.Integer(
        string="Doctor Count", store=False,
        compute='_compute_doctor_count',
    )
    
    is_doctor = fields.Boolean(
        string="Doctor", store=False,
        search='_search_is_doctor',
    )

    @api.depends('doctor_id')
    def _compute_doctor_count(self):
        for partner in self:
            partner.doctor_count = partner.doctor_id
        return

    def _search_is_doctor(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('doctor_id', search_operator, False)]

    doctor_type = fields.Selection(
        [
            ("standalone", "Standalone Doctor"),
            ("attached", "Attached to existing Doctor"),
        ],
        compute="_compute_doctor_type",
        store=True,
        index=True,
        default="standalone",
    )

    @api.depends("doctor_id")
    def _compute_doctor_type(self):
        for rec in self:
            rec.doctor_type = "attached" if rec.doctor_id else "standalone"

    def _basedoctor_check_context(self, mode):
        """Remove "search_show_all_positions" for non-search mode.
        Keeping it in context can result in unexpected behaviour (ex: reading
        one2many might return wrong result - i.e with "attached doctor"
        removed even if it"s directly linked to a company).
        Actually, is easier to override a dictionary value to indicate it
        should be ignored...
        """
        if mode != "search" and "search_show_all_positions" in self.env.context:
            result = self.with_context(
                search_show_all_positions={"is_set": False})
        else:
            result = self
        return result

    @api.model
    def create(self, vals):
        """When creating, use a modified self to alter the context (see
        comment in _basedoctor_check_context).  Also, we need to ensure
        that the name on an attached doctor is the same as the name on the
        doctor it is attached to."""
        modified_self = self._basedoctor_check_context("create")
        if not vals.get("name") and vals.get("doctor_id"):
            vals["name"] = modified_self.browse(vals["doctor_id"]).name
        return super(Partner, modified_self).create(vals)

    def read(self, fields=None, load="_classic_read"):
        modified_self = self._basedoctor_check_context("read")
        return super(Partner, modified_self).read(fields=fields, load=load)

    def write(self, vals):
        modified_self = self._basedoctor_check_context("write")
        return super(Partner, modified_self).write(vals)

    def unlink(self):
        modified_self = self._basedoctor_check_context("unlink")
        return super(Partner, modified_self).unlink()

    def _compute_commercial_partner(self):
        """Returns the partner that is considered the commercial
        entity of this partner. The commercial entity holds the master data
        for all commercial fields (see :py:meth:`~_commercial_fields`)"""
        result = super(Partner, self)._compute_commercial_partner()
        for partner in self:
            if partner.doctor_type == "attached" and not partner.parent_id:
                partner.commercial_partner_id = partner.doctor_id
        return result

    def _doctor_fields(self):
        """Returns the list of doctor fields that are synced from the parent
        when a partner is attached to him."""
        return ["name", "title"]

    def _doctor_sync_from_parent(self):
        """Handle sync of doctor fields when a new parent doctor entity
        is set, as if they were related fields
        """
        self.ensure_one()
        if self.doctor_id:
            doctor_fields = self._doctor_fields()
            sync_vals = self.doctor_id._update_fields_values(
                doctor_fields)
            self.write(sync_vals)

    def update_doctor(self, vals):
        if self.env.context.get("__update_doctor_lock"):
            return
        doctor_fields = self._doctor_fields()
        doctor_vals = {field: vals[field]
                             for field in doctor_fields if field in vals}
        if doctor_vals:
            self.with_context(__update_doctor_lock=True).write(
                doctor_vals)

    def _fields_sync(self, update_values):
        """Sync commercial fields and address fields from company and to
        children, doctor fields from doctor and to attached doctor
        after create/update, just as if those were all modeled as
        fields.related to the parent
        """
        self.ensure_one()
        super(Partner, self)._fields_sync(update_values)
        doctor_fields = self._doctor_fields()
        # 1. From UPSTREAM: sync from parent doctor
        if update_values.get("doctor_id"):
            self._doctor_sync_from_parent()
        # 2. To DOWNSTREAM: sync doctor fields to parent or related
        elif any(field in doctor_fields for field in update_values):
            update_ids = self.other_doctor_ids.filtered(
                lambda p: not p.is_company)
            if self.doctor_id:
                update_ids |= self.doctor_id
            update_ids.update_doctor(update_values)

    @api.onchange("doctor_id")
    def _onchange_doctor_id(self):
        if self.doctor_id:
            self.name = self.doctor_id.name

    @api.onchange("doctor_type")
    def _onchange_doctor_type(self):
        if self.doctor_type == "standalone":
            self.doctor_id = False

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
