# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime

# classes under  menu of laboratry


class lab_test_create(models.TransientModel):
    _name = "lab.test.create"
    _description = "pod lab test create"

    def create_lab_test(self):
        res_ids = []
        lab_rqu_obj = self.env["patient.lab.test"]
        browse_records = lab_rqu_obj.browse(self._context.get("active_ids"))
        result = {}
        for browse_record in browse_records:
            lab_obj = self.env["lab"]
            res = lab_obj.create(
                {
                    "name": self.env["ir.sequence"].next_by_code("ltest_seq"),
                    "patient_id": browse_record.patient_id.id or False,
                    "date_requested": browse_record.date or False,
                    "test_id": browse_record.test_type_id.id or False,
                    "requestor_physician_id": browse_record.doctor_id.id or False,
                }
            )
            res_ids.append(res.id)
            if res_ids:
                imd = self.env["ir.model.data"]
                write_ids = lab_rqu_obj.browse(self._context.get("active_id"))
                write_ids.write({"state": "tested"})
                action = self.env.ref("pod_mgmt_system.action_lab_tree")
                list_view_id = imd._xmlid_to_res_id("pod_mgmt_system.lab_tree_view")
                form_view_id = imd._xmlid_to_res_id("pod_mgmt_system.lab_form_view")
                result = {
                    "name": action.name,
                    "help": action.help,
                    "type": action.type,
                    "views": [[list_view_id, "tree"], [form_view_id, "form"]],
                    "target": action.target,
                    "context": action.context,
                    "res_model": action.res_model,
                    "res_id": res.id,
                }
            if res_ids:
                result["domain"] = "[('id','=',%s)]" % res_ids

        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
