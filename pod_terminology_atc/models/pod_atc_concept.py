# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PodiatryATCConcept(models.Model):
    """
    Podiatry ATC concept
    (https://www.hl7.org/fhir/terminologies-systems.html)
    It has been defined following the code system entity with the following
    information:
    - url: http://www.whocc.no/atc
    - identifier: urn:oid:2.16.840.1.113883.6.73
    - name: ATC/DDD
    - publisher: WHO
    """

    _name = "pod.atc.concept"
    _inherit = "pod.abstract.concept.uniparent"
    _parent_order = False
    _description = "pod atc concept"

    code = fields.Char(compute="_compute_code", store=True, required=False)
    level_code = fields.Char(required=True)
    parent_id = fields.Many2one(comodel_name="pod.atc.concept")
    child_ids = fields.One2many(comodel_name="pod.atc.concept")

    @api.depends("level_code", "parent_id")
    def _compute_code(self):
        for record in self:
            record.code = record.level_code
            if record.parent_id:
                record.code = record.parent_id.code + record.code
