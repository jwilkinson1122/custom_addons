# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PodiatryRequestGroup(models.Model):

    _inherit = "pod.request.group"

    def check_authorization_action(self):
        result = super(PodiatryRequestGroup, self).check_authorization_action()
        if (
            not self.authorization_method_id.check_required
            or not self.authorization_checked
        ):
            return result
        new_result = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_authorization."
            "pod_request_group_uncheck_authorization_act_window"
        )
        new_result["context"] = result["context"]
        return new_result
