# -*- coding: utf-8 -*-
import logging

import base64
import collections
import datetime
import hashlib
import pytz
import threading
import re

import requests
from collections import defaultdict
from lxml import etree
from random import randint
from werkzeug import urls

from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import RedirectWarning, UserError, ValidationError


_logger = logging.getLogger(__name__)

ADDRESS_FIELDS = ("street", "street2", "zip", "city", "state_id", "country_id")


@api.model
def _lang_get(self):
    return self.env["res.lang"].get_installed()


# put POSIX 'Etc/*' entries at the end to avoid confusing users - see bug 1086728
_tzs = [
    (tz, tz)
    for tz in sorted(
        pytz.all_timezones, key=lambda tz: tz if not tz.startswith("Etc/") else "_"
    )
]


def _tz_get(self):
    return _tzs


# class Practice(models.Model):
#     _name = "res.practice"
#     _inherit = ["format.address.mixin", "avatar.mixin"]
#     _description = "Company Practices"
#     _order = "complete_practice_name ASC, id DESC"

#     active = fields.Boolean(default=True)
#     name = fields.Char(index=True, required=True)
#     practice_name = fields.Char("Practice Name")
#     complete_practice_name = fields.Char(
#         compute="_compute_complete_practice_name", store=True, index=True
#     )
#     date = fields.Date(index=True)
#     partner_id = fields.Many2one(
#         "res.partner",
#         string="Customer",
#         store=True,
#         domain="[('is_practice_partner', '=', True)]",
#     )
#     parent_practice_id = fields.Many2one(
#         "res.practice",
#         string="Parent Practice",
#         store=True,
#         help="Parent practice, if any.",
#     )
#     contact_ids = fields.One2many(
#         "res.practice.contact", "practice_id", string="Contacts", tracking=True
#     )
#     manager_id = fields.Many2one("res.partner", compute="_compute_manager", store=True)
#     primary_physician_id = fields.Many2one(
#         "res.partner",
#         compute="_compute_primary_physician",
#         store=True,
#         string="Primary Physician",
#     )
#     patient_ids = fields.Many2many(
#         "res.patient",
#         relation="res_practice_patient_rel",
#         column1="practice_id",
#         column2="patient_id",
#         tracking=True,
#         string="Patients",
#     )
#     patient_count = fields.Integer(compute="_compute_patient_count")

#     _sql_constraints = [
#         ("name_uniq", "unique (name)", "The Practice name must be unique!")
#     ]

#     @api.model_create_multi
#     def create(self, vals_list):
#         for vals in vals_list:
#             vals["partner_id"] = (
#                 self.env["res.partner"]
#                 .create(
#                     {
#                         "name": vals.get("name"),
#                         "is_practice_partner": True,
#                         "is_company": True,
#                     }
#                 )
#                 .id
#             )
#         return super().create(vals_list)

#     def write(self, vals):
#         previous_patient_ids = self.sudo().patient_ids
#         res = super().write(vals)
#         if "contact_ids" in vals or "patient_ids" in vals:
#             (self.sudo().patient_ids | previous_patient_ids).recompute_followers()
#         return res

#     def unlink(self):
#         to_recompute = self.patient_ids
#         res = super().unlink()
#         to_recompute.recompute_followers()
#         return res

#     @api.depends("patient_ids.is_active")
#     def _compute_patient_count(self):
#         for rec in self:
#             rec.patient_count = len(rec.patient_ids)


# class PracticeContact(models.Model):
#     _name = "res.practice.contact"
#     _description = "Practice Contact"

#     sequence = fields.Integer()
#     practice_id = fields.Many2one("res.practice", required=True, ondelete="cascade")
#     partner_id = fields.Many2one(
#         "res.partner",
#         required=True,
#         ondelete="cascade",
#         domain=[("is_company", "=", False)],
#     )
#     role = fields.Selection(
#         selection=[
#             ("manager", "Practice Manager"),
#             ("primary_physician", "Primary Physician"),
#             ("assistant", "Assistant"),
#             ("physician", "Physician"),
#             ("orthotist", "Orthotist"),
#             ("therapist", "Physical Therapist"),
#             ("nurse", "Nurse"),
#             ("receptionist", "Receptionist"),
#             ("administrative", "Administrative"),
#             ("other", "Other"),
#         ],
#         required=True,
#     )

#     @api.constrains("role")
#     def _constrain_role(self):
#         unique_roles = {"manager": "Practice Manager"}
#         for rec in self:
#             for role_key, role_name in unique_roles.items():
#                 if (
#                     len(
#                         rec.practice_id.contact_ids.filtered(
#                             lambda r: r.role == role_key
#                         )
#                     )
#                     > 1
#                 ):
#                     raise ValidationError(
#                         _("A practice can have only one %s.") % role_name
#                     )


class Practice(models.Model):
    _name = "res.practice"
    _inherit = ["format.address.mixin", "avatar.mixin"]
    _description = "Company Practices"
    _order = "complete_practice_name ASC, id DESC"
    _rec_names_search = ["complete_practice_name", "email", "ref"]

    _complete_name_displayed_practice_types = (
        "private",
        "clinic",
        "hospital",
        "distributor",
        "specialty",
        "other",
    )
    _complete_name_displayed_address_types = ("invoice", "delivery", "other")

    active = fields.Boolean(default=True)

    name = fields.Char(index=True, default_export_compatible=True)
    practice_name = fields.Char("Practice Name")
    complete_practice_name = fields.Char(
        compute="_compute_complete_practice_name", store=True, index=True
    )

    date = fields.Date(index=True)

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        store=True,
        domain="[('is_practice_partner', '=', True)]",
    )
    parent_practice_id = fields.Many2one(
        "res.practice",
        string="Parent Practice",
        help="The parent practice of this practice, if any.",
        store=True,
    )
    parent_practice_name = fields.Char(
        related="parent_practice_id.name", readonly=True, string="Parent name"
    )

    child_practice_ids = fields.One2many(
        "res.practice",
        "parent_practice_id",
        string="Child Practices",
        help="Practices under this practice.",
    )

    ref = fields.Char(string="Reference", index=True)
    contact_ids = fields.One2many(
        comodel_name="res.practice.contact",
        inverse_name="practice_id",
        tracking=True,
    )
    manager_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_manager",
        store=True,
    )
    manager_name = fields.Char(
        related="manager_id.name",
        string="Practice Manager Name",
    )
    primary_physician_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_primary_physician",
        store=True,
        string="Primary Physician",
    )
    primary_physician_name = fields.Char(
        related="primary_physician_id.name",
        string="Primary Physician Name",
    )

    user_id = fields.Many2one(
        "res.users",
        string="Internal User",
        compute="_compute_user_id",
        precompute=True,
        readonly=False,
        store=True,
        help="Internal system user.",
    )
    allowed_user_ids = fields.Many2many(
        comodel_name="res.users",
        compute="_compute_allowed_user_ids",
        inverse="_inverse_allowed_user_ids",
    )
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one(
        "res.country.state",
        string="Fed. State",
        domain="[('country_id', '=?', country_id)]",
    )
    country_id = fields.Many2one("res.country", string="Country")
    country_code = fields.Char(related="country_id.code", string="Country Code")
    practice_latitude = fields.Float(string="Geo Latitude", digits=(10, 7))
    practice_longitude = fields.Float(string="Geo Longitude", digits=(10, 7))
    email = fields.Char(store=True)
    phone = fields.Char(store=True, unaccent=False)
    mobile = fields.Char(store=True, unaccent=False)
    website = fields.Char()

    practice_type = fields.Selection(
        [
            ("private", "Private"),
            ("clinic", "Clinic"),
            ("hospital", "Hospital"),
            ("distributor", "Distributor"),
            ("specialty", "Specialty"),
            ("other", "Other"),
        ],
        string="Practice Type",
        default="",
    )

    address_type = fields.Selection(
        [
            ("invoice", "Invoice Address"),
            ("delivery", "Delivery Address"),
            ("other", "Other Address"),
        ],
        string="Address Type",
        default="",
    )

    color = fields.Integer(string="Color Index", default=0)

    patient_ids = fields.Many2many(
        comodel_name="res.patient",
        relation="res_practice_patient_rel",
        column1="practice_id",
        column2="patient_id",
        string="Patients",
        tracking=True,
    )

    patient_count = fields.Integer(compute="_compute_patient_counts")

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The Practice name must be unique!")
    ]

    @api.model_create_multi
    def create(self, vals):
        partner_vals = {
            "name": vals.get("name"),
            "is_practice_partner": True,
            "is_company": True,
        }
        partner = self.env["res.partner"].create(partner_vals)
        vals["partner_id"] = partner.id
        for index, rec in enumerate(vals):
            if "contact_ids" in partner_vals[index]:
                rec.sudo().patient_ids.recompute_followers()
        return super(Practice, self).create(vals)

    def write(self, vals):
        previous_patient_ids = self.sudo().patient_ids
        res = super().write(vals)
        if "contact_ids" in vals or "patient_ids" in vals:
            (self.sudo().patient_ids | previous_patient_ids).recompute_followers()
        return res

    def unlink(self):
        to_recompute = self.patient_ids
        res = super().unlink()
        to_recompute.recompute_followers()
        return res

    @api.depends("patient_ids.is_active")
    def _compute_patient_counts(self):
        for rec in self:
            rec.patient_count = len(rec.patient_ids)
            rec.inactive_count = len(rec.patient_ids.filtered(lambda p: p.is_active))
            rec.active_count = rec.patient_count - rec.inactive_count

    @api.depends("contact_ids.role")
    def _compute_manager(self):
        for rec in self:
            contact = rec.contact_ids.filtered(lambda r: r.role == "manager")
            rec.manager_id = contact.partner_id if contact else False

    @api.depends("contact_ids.role")
    def _compute_primary_physician(self):
        for rec in self:
            contact = rec.contact_ids.filtered(lambda r: r.role == "primary_physician")
            rec.primary_physician_id = contact.partner_id if contact else False

    def _compute_allowed_user_ids(self):
        for rec in self:
            rec.allowed_user_ids = rec.contact_ids.user_ids

    def _inverse_allowed_user_ids(self):
        for rec in self:
            removed_contact = rec.contact_ids.filtered(
                lambda contact: contact.user_ids not in rec.allowed_user_ids
            )
            added_users = rec.allowed_user_ids - rec.contact_ids.user_ids
            removed_contact.unlink()
            self.env["res.practice.contact"].create(
                [
                    {
                        "practice_id": rec.id,
                        "partner_id": user.partner_id.id,
                        "role": "other",
                    }
                    for user in added_users
                ]
            )

    def remove_access(self, user):
        self.contact_ids.filtered(lambda contact: user in contact.user_ids).unlink()


class PracticeContact(models.Model):
    _name = "res.practice.contact"
    _description = "Podiatry Practice Contact"

    sequence = fields.Integer()
    practice_id = fields.Many2one(
        comodel_name="res.practice",
        string="Practice",
        required=True,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Contacts",
        required=True,
        domain=[("is_company", "=", False)],
        ondelete="cascade",
    )
    active = fields.Boolean(related="partner_id.active")
    role = fields.Selection(
        selection=[
            ("manager", "Practice Manager"),
            ("primary_physician", "Primary Physician"),
            ("assistant", "Assistant"),
            ("physician", "Physician"),
            ("orthotist", "Orthotist"),
            ("therapist", "Physical Therapist"),
            ("nurse", "Nurse"),
            ("receptionist", "Receptionist"),
            ("administrative", "Administrative"),
            ("other", "Other"),
        ],
        required=True,
    )

    mobile = fields.Char(related="partner_id.mobile", readonly=False)
    name = fields.Char(related="partner_id.name", readonly=False)
    parent_id = fields.Many2one(
        related="partner_id.parent_id",
        readonly=False,
        string="Organization",
        domain=[("is_company", "=", True)],
    )
    email = fields.Char(related="partner_id.email", readonly=False)
    user_ids = fields.One2many(related="partner_id.user_ids", readonly=True)
    has_portal_access = fields.Boolean(
        compute="_compute_has_portal_access", compute_sudo=True
    )

    _sql_constraints = [
        (
            "practice_contact_unique",
            "unique(practice_id, partner_id)",
            "Each partner can only be related to a given practice once.",
        )
    ]

    @api.constrains("role")
    def _constrain_role(self):
        unique_roles = {
            "manager": "Practice Manager",
        }

        practices = self.mapped("practice_id")
        for practice in practices:
            for role_key, role_name in unique_roles.items():
                role_count = len(
                    practice.contact_ids.filtered(lambda r: r.role == role_key)
                )
                if role_count > 1:
                    raise ValidationError(
                        _("A practice can have only one %s.") % role_name
                    )

    @api.onchange("mobile")
    def _onchange_mobile_validation(self):
        if self.mobile:
            self.mobile = self.partner_id._phone_format(
                self.mobile, force_format="INTERNATIONAL"
            )

    @api.depends("user_ids", "user_ids.groups_id")
    def _compute_has_portal_access(self):
        for rec in self:
            rec.has_portal_access = (
                bool(rec.user_ids.filtered(lambda r: r.has_group("base.group_portal")))
                or bool(rec.user_ids.filtered(lambda r: r.has_group("base.group_user")))
                or bool(rec.partner_id.signup_token)
            )

    def action_revoke_portal_access(self):
        group_portal = self.env.ref("base.group_portal")
        group_public = self.env.ref("base.group_public")
        self.user_ids.write(
            {
                "groups_id": [
                    Command.unlink(group_portal.id),
                    Command.link(group_public.id),
                ],
                "active": False,
            }
        )
        self.partner_id.sudo().signup_token = False

    def action_grant_portal_access(self):
        wiz = self.env["portal.wizard"].create(
            {"partner_ids": [(4, self.partner_id.id)]}
        )
        return wiz._action_open_modal()

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.practice_id.mapped("patient_ids").recompute_followers()
        return res

    def unlink(self):
        patients = self.practice_id.mapped("patient_ids")
        res = super().unlink()
        patients.recompute_followers()
        return res

    def write(self, values):
        if "practice_id" in values:
            to_recompute = self.env["res.patient"]
            for rec in self:
                if rec.practice_id.id != values["practice_id"]:
                    to_recompute |= rec.practice_id.patient_ids
            res = super().write(values)
            to_recompute.recompute_followers()
            return res
        return super().write(values)
