# -*- coding: utf-8 -*-

import re
from urllib.parse import parse_qs, urlencode, urlparse

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

NWPL_ROOT_URL = "https://erp.nwpodiatric.com"


# https://erp.nwpodiatric.com/
# https://nwpodiatric.com/
# https://nwpodiatric.com/provider-search/
class ResPartner(models.Model):
    _inherit = "res.partner"

    nwpl_membership_number = fields.Char(
        "NWPL Membership Number",
        copy=False,
        help="NWPL membership number of the player.\nUsually looks like 300xxxxx.",
    )
    nwpl_uuid = fields.Char(
        "NWPL UUID",
        inverse="_inverse_nwpl_uuid",
        copy=False,
        help="NWPL UUID of the player/practice. Can also be any valid URL:\n"
        "i.e. #1: https://erp.nwpodiatric.com/<UUID>\n",
    )
    nwpl_external_url = fields.Char(
        "NWPL External URL",
        compute="_compute_nwpl_url",
        help="Player/practice external link (do not require any authentication).",
    )
    nwpl_internal_url = fields.Char(
        "NWPL Internal URL",
        compute="_compute_nwpl_url",
        help="Player/practice internal link (require an authentication with practice admin account).",
    )

    @api.depends("nwpl_uuid")
    def _compute_nwpl_url(self):
        for record in self:
            if not record.nwpl_uuid:
                record.nwpl_external_url = ""
                record.nwpl_internal_url = ""
            else:
                int_mid_url = (
                    "association/group" if record.is_company else "player-profile"
                )
                record.nwpl_external_url = (
                    f"{NWPL_ROOT_URL}/{int_mid_url}/{record.nwpl_uuid}"
                )
                ext_id_key, end_url = (
                    ("gid", "group.aspx")
                    if record.is_company
                    else ("mid", "member.aspx")
                )
                url_params = urlencode({ext_id_key: record.nwpl_uuid})
                record.nwpl_internal_url = (
                    f"{NWPL_ROOT_URL}/organization/{end_url}?{url_params}"
                )

    @api.constrains("nwpl_membership_number")
    def _check_nwpl_membership_number(self):
        """Checks that the number of the NWPL membership is unique.

        :return: None
        """
        for record in self:
            if (
                record.nwpl_membership_number
                and self.search_count(
                    [("nwpl_membership_number", "=", record.nwpl_membership_number)]
                )
                > 1
            ):
                raise ValidationError(
                    _(
                        "The NWPL membership number must be unique! "
                        "Please change it accordingly or leave it empty."
                    )
                )

    @api.constrains("nwpl_uuid")
    def _check_nwpl_uuid(self):
        """Checks that the external UUID of the NWPL membership is unique and well formatted.

        :return: None
        """
        regex = re.compile(
            "^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z",
            re.I,
        )
        for record in self:
            if not record.nwpl_uuid:
                continue
            if not regex.match(record.nwpl_uuid):
                raise ValidationError(
                    _(
                        "The %s ('%s') does not match the UUID4 format.\n"
                        "It should look like 'xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx' or any valid URL from %s.",
                        record._fields["nwpl_uuid"].string,
                        record.nwpl_uuid,
                        NWPL_ROOT_URL,
                    )
                )
            if self.search_count([("nwpl_uuid", "=", record.nwpl_uuid)]) > 1:
                raise ValidationError(
                    _(
                        "The %s must be unique! Please change it accordingly or leave it empty.",
                        record._fields["nwpl_uuid"].string,
                    )
                )

    def _inverse_nwpl_uuid(self):
        for record in self:
            url_parsed = urlparse(record.nwpl_uuid)
            if urlparse(NWPL_ROOT_URL).netloc != url_parsed.netloc:
                continue
            paths = url_parsed.path.split("/")
            ext_uuid = None

            if record.is_company:
                if url_parsed.path == "/organization/group.aspx":
                    ext_uuid = parse_qs(url_parsed.query).get("gid", [""])[0]
                elif "/association/group" in url_parsed.path:
                    ext_uuid = paths[paths.index("group") + 1]
            else:
                if url_parsed.path == "/organization/member.aspx":
                    ext_uuid = parse_qs(url_parsed.query).get("mid", [""])[0]
                elif "player-profile" in paths:
                    ext_uuid = paths[paths.index("player-profile") + 1]

            if not ext_uuid:
                raise ValidationError(
                    _(
                        "It is not possible to get the UUID for URL section '%s'.",
                        url_parsed.path,
                    )
                )
            record.nwpl_uuid = ext_uuid
