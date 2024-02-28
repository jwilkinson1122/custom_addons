# -*- coding: utf-8 -*-


from odoo import fields, models, api


class SpreadsheetContributor(models.Model):
    _name = "spreadsheet.contributor"
    _description = "Spreadsheet Contributor"
    _rec_name = 'user_id'

    prescription_id = fields.Many2one("prescriptions.prescription")
    user_id = fields.Many2one("res.users")
    last_update_date = fields.Datetime("Last update date", default=fields.Datetime.now)

    _sql_constraints = [
        (
            "spreadsheet_user_unique",
            "unique (prescription_id, user_id)",
            "A combination of the spreadsheet and the user already exist",
        ),
    ]

    @api.model
    def _update(self, user, prescription):
        record = self.search(
            [("user_id", "=", user.id), ("prescription_id", "=", prescription.id)]
        )
        if record:
            record.write({"last_update_date": fields.Datetime.now()})
        else:
            self.create(
                {
                    "prescription_id": prescription.id,
                    "user_id": user.id,
                }
            )
