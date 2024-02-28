# -*- coding: utf-8 -*-

from odoo import fields, models, _

class SpreadsheetTemplate(models.Model):
    _name = "spreadsheet.template"
    _inherit = "spreadsheet.mixin"
    _description = "Spreadsheet Template"
    _order = "sequence"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=100)

    def copy(self, default=None):
        self.ensure_one()
        chosen_name = default.get("name") if default else None
        new_name = chosen_name or _("%s (copy)", self.name)
        default = dict(default or {}, name=new_name)
        return super().copy(default)

    def action_edit_template(self):
        self.ensure_one()
        return {
            "type": "ir.actions.client",
            "tag": "action_open_template",
            "params": {
                "spreadsheet_id": self.id,
            },
        }

    def action_create_spreadsheet(self, prescription_vals=None):
        if prescription_vals is None:
            prescription_vals = {}
        self.ensure_one()
        spreadsheet = self.env["prescriptions.prescription"].create({
            "name": self.name,
            "mimetype": "application/o-spreadsheet",
            "handler": "spreadsheet",
            "spreadsheet_data": self.spreadsheet_data,
            **prescription_vals,
        })
        spreadsheet.spreadsheet_snapshot = self.spreadsheet_snapshot
        self._copy_revisions_to(spreadsheet)

        update_locale_command = {
            "type": "UPDATE_LOCALE",
            "locale": self.env["res.lang"]._get_user_spreadsheet_locale(),
        }
        spreadsheet._dispatch_command(update_locale_command)

        return {
            "type": "ir.actions.client",
            "tag": "action_open_spreadsheet",
            "params": {
                "spreadsheet_id": spreadsheet.id,
                "convert_from_template": True,
            },
        }

    def action_edit(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'action_open_template',
            'params': {
                'spreadsheet_id': self.id,
            }
        }

    def _creation_msg(self):
        return _("New spreadsheet template created")
