from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_patient_add_plan_definition = fields.Boolean(
        string="Add Plan definition on patients",
        implied_group="pod_workflow." "group_patient_add_plan_definition",
    )

    group_main_activity_plan_definition = fields.Boolean(
        string="Allows to add a main activity definition on a plan definition",
        implied_group="pod_workflow."
        "group_main_activity_plan_definition",
    )
