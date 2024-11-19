# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError

# classes under  menu of laboratry


class patient_lab_test(models.Model):
    _name = "patient.lab.test"
    _description = "pod patient lab test"
    _rec_name = "test_type_id"

    request = fields.Char("Request", readonly=True)
    date = fields.Datetime("Date", default=fields.Datetime.now)
    lab_test_owner_partner_id = fields.Many2one("res.partner", "Owner Name")
    urgent = fields.Boolean(
        "Urgent",
    )
    owner_partner_id = fields.Many2one("res.partner")
    state = fields.Selection(
        [("draft", "Draft"), ("tested", "Tested"), ("cancel", "Cancel")],
        readonly=True,
        default="draft",
    )
    test_type_id = fields.Many2one("test_type", "Test Type", required=True)
    patient_id = fields.Many2one("patient", "Patient")
    doctor_id = fields.Many2one("physician", "Doctor", required=True)
    insurer_id = fields.Many2one("insurance", "Insurer")
    invoice_to_insurer = fields.Boolean("Invoice to Insurance")
    lab_res_created = fields.Boolean(default=False)
    is_invoiced = fields.Boolean(copy=False, default=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["request"] = self.env["ir.sequence"].next_by_code("test_seq")
        return super(patient_lab_test, self).create(vals_list)

    def cancel_lab_test(self):
        self.write({"state": "cancel"})

    def create_lab_test(self):
        res_ids = []
        for browse_record in self:
            result = {}
            lab_obj = self.env["lab"]
            res = lab_obj.create(
                {
                    "name": self.env["ir.sequence"].next_by_code("ltest_seq"),
                    "patient_id": browse_record.patient_id.id,
                    "date_requested": browse_record.date or False,
                    "test_id": browse_record.test_type_id.id or False,
                    "requestor_physician_id": browse_record.doctor_id.id or False,
                }
            )
            res_ids.append(res.id)
            if res_ids:
                imd = self.env["ir.model.data"]
                action = self.env.ref("pod_mgmt_system.action_lab_form")
                list_view_id = imd.sudo()._xmlid_to_res_id(
                    "pod_mgmt_system.lab_tree_view"
                )
                form_view_id = imd.sudo()._xmlid_to_res_id(
                    "pod_mgmt_system.lab_form_view"
                )
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
