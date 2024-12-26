# -*- coding: utf-8 -*-
from datetime import date

from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models, tools


class Partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    is_location = fields.Boolean("Practice")
    is_practitioner = fields.Boolean("Practitioner")
    is_patient = fields.Boolean("Patient")
    reference = fields.Char("ID Number")

    info_ids = fields.One2many("res.partner.info", "partner_id", string="More Info")

    prescription_count = fields.Integer(compute="get_prescription_count")

    name = fields.Char(index=True)

    patient_ids = fields.One2many(
        comodel_name="podiatry.patient",
        inverse_name="partner_id",
        string="Patients",
    )

    patient_count = fields.Integer(
        string="Patient Count",
        store=False,
        compute="_compute_patient_count",
    )

    @api.depends("patient_ids")
    def _compute_patient_count(self):
        for partner in self:
            partner.patient_count = partner.patient_ids
        return

    def open_customer_prescriptions(self):
        for records in self:
            return {
                "name": _("Prescription"),
                "view_type": "form",
                "domain": [("customer", "=", records.id)],
                "res_model": "podiatry.prescription",
                "view_id": False,
                "view_mode": "tree,form",
                "context": {"default_customer": self.id},
                "type": "ir.actions.act_window",
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env["podiatry.prescription"].search_count(
                [("customer", "=", records.id)]
            )
            records.prescription_count = count

    practitioner_id = fields.Many2one(
        "res.partner",
        string="Main Practitioner",
        domain=[("is_company", "=", False), ("practitioner_type", "=", "standalone")],
    )

    other_practitioner_ids = fields.One2many(
        "res.partner",
        "practitioner_id",
        string="Others Positions",
    )

    practitioner_count = fields.Integer(
        string="Practitioner Count",
        store=False,
        compute="_compute_practitioner_count",
    )

    @api.depends("practitioner_id")
    def _compute_practitioner_count(self):
        for partner in self:
            partner.practitioner_count = partner.practitioner_id
        return

    practitioner_type = fields.Selection(
        [
            ("standalone", "Standalone Practitioner"),
            ("attached", "Attached to existing Practitioner"),
        ],
        compute="_compute_practitioner_type",
        store=True,
        index=True,
        default="standalone",
    )

    @api.depends("practitioner_id")
    def _compute_practitioner_type(self):
        for rec in self:
            rec.practitioner_type = "attached" if rec.practitioner_id else "standalone"

    def _basepractitioner_check_context(self, mode):
        if mode != "search" and "search_show_all_positions" in self.env.context:
            result = self.with_context(search_show_all_positions={"is_set": False})
        else:
            result = self
        return result

    @api.model
    def create(self, vals):
        modified_self = self._basepractitioner_check_context("create")
        if not vals.get("name") and vals.get("practitioner_id"):
            vals["name"] = modified_self.browse(vals["practitioner_id"]).name
        return super(Partner, modified_self).create(vals)

    def read(self, fields=None, load="_classic_read"):
        modified_self = self._basepractitioner_check_context("read")
        return super(Partner, modified_self).read(fields=fields, load=load)

    def write(self, vals):
        modified_self = self._basepractitioner_check_context("write")
        return super(Partner, modified_self).write(vals)

    def unlink(self):
        modified_self = self._basepractitioner_check_context("unlink")
        return super(Partner, modified_self).unlink()

    def _compute_commercial_partner(self):
        result = super(Partner, self)._compute_commercial_partner()
        for partner in self:
            if partner.practitioner_type == "attached" and not partner.parent_id:
                partner.commercial_partner_id = partner.practitioner_id
        return result

    def _practitioner_fields(self):
        return ["name", "title"]

    def _practitioner_sync_from_parent(self):
        self.ensure_one()
        if self.practitioner_id:
            practitioner_fields = self._practitioner_fields()
            sync_vals = self.practitioner_id._update_fields_values(practitioner_fields)
            self.write(sync_vals)

    def update_practitioner(self, vals):
        if self.env.context.get("__update_practitioner_lock"):
            return
        practitioner_fields = self._practitioner_fields()
        practitioner_vals = {
            field: vals[field] for field in practitioner_fields if field in vals
        }
        if practitioner_vals:
            self.with_context(__update_practitioner_lock=True).write(practitioner_vals)

    def _fields_sync(self, update_values):
        self.ensure_one()
        super(Partner, self)._fields_sync(update_values)
        practitioner_fields = self._practitioner_fields()
        # 1. From UPSTREAM: sync from parent practitioner
        if update_values.get("practitioner_id"):
            self._practitioner_sync_from_parent()
        # 2. To DOWNSTREAM: sync practitioner fields to parent or related
        elif any(field in practitioner_fields for field in update_values):
            update_ids = self.other_practitioner_ids.filtered(
                lambda p: not p.is_company
            )
            if self.practitioner_id:
                update_ids |= self.practitioner_id
            update_ids.update_practitioner(update_values)

    @api.onchange("practitioner_id")
    def _onchange_practitioner_id(self):
        if self.practitioner_id:
            self.name = self.practitioner_id.name

    @api.onchange("practitioner_type")
    def _onchange_practitioner_type(self):
        if self.practitioner_type == "standalone":
            self.practitioner_id = False

    @api.model
    def create_partner_from_ui(self, partner, extraPartner):
        """create or modify a partner from the point of sale ui.
        partner contains the partner's fields."""
        # image is a dataurl, get the data after the comma
        extraPartner_id = partner.pop("id", False)
        if extraPartner:
            if extraPartner.get("image_1920"):
                extraPartner["image_1920"] = extraPartner["image_1920"].split(",")[1]
            if extraPartner_id:  # Modifying existing extraPartner
                custom_info = self.env["custom.partner.field"].search([])
                for i in custom_info:
                    if i.name in extraPartner.keys():
                        info_data = self.env["res.partner.info"].search(
                            [
                                ("partner_id", "=", extraPartner_id),
                                ("name", "=", i.name),
                            ]
                        )
                        if info_data:
                            info_data.write(
                                {
                                    "info_name": extraPartner[i.name],
                                    "partner_id": extraPartner_id,
                                }
                            )
                        else:
                            self.browse(extraPartner_id).write(
                                {
                                    "info_ids": [
                                        (
                                            0,
                                            0,
                                            {
                                                "name": i.name,
                                                "info_name": extraPartner[i.name],
                                            },
                                        )
                                    ]
                                }
                            )
            else:
                extraPartner_id = self.create(extraPartner).id

        if partner:
            if partner.get("image_1920"):
                partner["image_1920"] = partner["image_1920"].split(",")[1]
            if extraPartner_id:  # Modifying existing partner

                self.browse(extraPartner_id).write(partner)
            else:
                extraPartner_id = self.create(partner).id
        return extraPartner_id


class CustomPartnerField(models.Model):
    _name = "custom.partner.field"

    name = fields.Char(string="Custom Partner Fields")


class ResPartnerInfo(models.Model):
    _name = "res.partner.info"

    name = fields.Char(string="Extra Info", required=True)
    info_name = fields.Char(string="Info Name")
    partner_id = fields.Many2one("res.partner", string="Partner Info")
    field_id = fields.Many2one("custom.partner.field", string="Custom Filed")
