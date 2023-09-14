

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def unlink(self):
        sale_lines = self.mapped("sale_line_ids")
        res = super().unlink()
        sale_lines.write({"preinvoice_group_id": False})
        return res
