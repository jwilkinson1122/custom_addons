# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_pod_careplan_add_plan_definition = fields.Boolean(
        string="Add Plan definition on careplans",
        implied_group="pod_clinical_careplan."
        "group_pod_careplan_add_plan_definition",
    )
