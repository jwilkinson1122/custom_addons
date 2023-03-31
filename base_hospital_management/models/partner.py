# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools


class Partner(models.Model):
    _inherit = 'res.partner'
    _description = "Patient"
    
    info_ids = fields.One2many(
        'res.partner.info', 'partner_id', string="More Info")
    name = fields.Char(index=True)
    is_patient = fields.Boolean(string='Is Patient')
    is_doctor = fields.Boolean(string='Is Physician')
    is_hospital = fields.Boolean(string='Is Hospital')
    specialty = fields.Many2one('doctor.specialty', string='Specialty')
    hospital = fields.Many2one('res.partner', string='Hospital')
    # pharmacy_id = fields.Many2one('hospital.pharmacy', string="Pharmacy")
    
    hospital_role = fields.Many2many(
        string="Job Roles", comodel_name="hospital.roles"
    )  # Field: HospitalRole/role

    
    hospital_id = fields.Many2one(
        "res.partner",
        string="Main Practice",
        domain=[("is_hospital", "=", True),
                ("hospital_type", "=", "standalone")],
    )

    other_hospital_ids = fields.One2many(
        "res.partner",
        "hospital_id",
        string="Others Positions",
    )

    hospital_count = fields.Integer(
        string="Hospital Count", store=False,
        compute='_compute_hospital_count',
    )

    @api.depends('hospital_id')
    def _compute_hospital_count(self):
        for partner in self:
            partner.hospital_count = partner.hospital_id
        return

    def _search_is_hospital(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('hospital_id', search_operator, False)]

    hospital_type = fields.Selection(
        [
            ("standalone", "Standalone Hospital"),
            ("attached", "Attached to existing Hospital"),
        ],
        compute="_compute_hospital_type",
        store=True,
        index=True,
        default="standalone",
    )

    @api.depends("hospital_id")
    def _compute_hospital_type(self):
        for rec in self:
            rec.hospital_type = "attached" if rec.hospital_id else "standalone"

    def _base_hospital_check_context(self, mode):
        """Remove "search_show_all_positions" for non-search mode.
        Keeping it in context can result in unexpected behavior (ex: reading
        one2many might return wrong result - i.e with "attached hospital"
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
        comment in _base_hospital_check_context).  Also, we need to ensure
        that the name on an attached hospital is the same as the name on the
        hospital it is attached to."""
        modified_self = self._base_hospital_check_context("create")
        if not vals.get("name") and vals.get("hospital_id"):
            vals["name"] = modified_self.browse(vals["hospital_id"]).name
        return super(Partner, modified_self).create(vals)

    def read(self, fields=None, load="_classic_read"):
        modified_self = self._base_hospital_check_context("read")
        return super(Partner, modified_self).read(fields=fields, load=load)

    def write(self, vals):
        modified_self = self._base_hospital_check_context("write")
        return super(Partner, modified_self).write(vals)

    def unlink(self):
        modified_self = self._base_hospital_check_context("unlink")
        return super(Partner, modified_self).unlink()

    def _compute_commercial_partner(self):
        """Returns the partner that is considered the commercial
        entity of this partner. The commercial entity holds the master data
        for all commercial fields (see :py:meth:`~_commercial_fields`)"""
        result = super(Partner, self)._compute_commercial_partner()
        for partner in self:
            if partner.hospital_type == "attached" and not partner.parent_id:
                partner.commercial_partner_id = partner.hospital_id
        return result

    def _hospital_fields(self):
        """Returns the list of hospital fields that are synced from the parent
        when a partner is attached to him."""
        return ["name", "title"]

    def _hospital_sync_from_parent(self):
        """Handle sync of hospital fields when a new parent hospital entity
        is set, as if they were related fields
        """
        self.ensure_one()
        if self.hospital_id:
            hospital_fields = self._hospital_fields()
            sync_vals = self.hospital_id._update_fields_values(
                hospital_fields)
            self.write(sync_vals)

    def update_hospital(self, vals):
        if self.env.context.get("__update_hospital_lock"):
            return
        hospital_fields = self._hospital_fields()
        hospital_vals = {field: vals[field]
                             for field in hospital_fields if field in vals}
        if hospital_vals:
            self.with_context(__update_hospital_lock=True).write(
                hospital_vals)

    def _fields_sync(self, update_values):
        """Sync commercial fields and address fields from company and to
        children, hospital fields from hospital and to attached hospital
        after create/update, just as if those were all modeled as
        fields.related to the parent
        """
        self.ensure_one()
        super(Partner, self)._fields_sync(update_values)
        hospital_fields = self._hospital_fields()
        # 1. From UPSTREAM: sync from parent hospital
        if update_values.get("hospital_id"):
            self._hospital_sync_from_parent()
        # 2. To DOWNSTREAM: sync hospital fields to parent or related
        elif any(field in hospital_fields for field in update_values):
            update_ids = self.other_hospital_ids.filtered(
                lambda p: not p.is_company)
            if self.hospital_id:
                update_ids |= self.hospital_id
            update_ids.update_hospital(update_values)

    @api.onchange("hospital_id")
    def _onchange_hospital_id(self):
        if self.hospital_id:
            self.name = self.hospital_id.name

    @api.onchange("hospital_type")
    def _onchange_hospital_type(self):
        if self.hospital_type == "standalone":
            self.hospital_id = False

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
 
#     company_type = fields.Selection([
#     ('person', 'Individual'),
#     ('company', 'Company'),
#     ], string='Company Type', default='company')
    
    
#     @api.model
# def get_default_auType(self):
#     default_auType = 'type1'
#     return default_auType

# auType = fields.Selection(selection=[('type1', 'Type 1'),('type2', 'Type 2'),], string='Type', default=get_default_auType)  



class CustomPartnerField(models.Model):
    _name = "custom.partner.field"

    name = fields.Char(string="Custom Partner Fields")
    # config_id = fields.Many2one("pos.config", string="Pos Config")


class ResPartnerInfo(models.Model):
    _name = "res.partner.info"

    name = fields.Char(string="Extra Info", required=True)
    info_name = fields.Char(string="Info Name")
    partner_id = fields.Many2one("res.partner", string="Partner Info")
    field_id = fields.Many2one("custom.partner.field", string="Custom Filed")