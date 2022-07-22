from odoo import fields, models


class Prescription(models.Model):
    """
    - Add support to RxID10
    """
    _inherit = "clinic.prescription"

    is_available = fields.Boolean("Is Available?")

    rx_id = fields.Char(help="Use a valid RxID-13 or RxID-10.")
    administrator_id = fields.Many2one(index=True)

    def _check_rx_id(self):
        self.ensure_one()
        digits = [int(x) for x in self.rx_id if x.isdigit()]
        if len(digits) == 10:
            ponderators = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            total = sum(a * b for a, b in zip(digits[:9], ponderators))
            check = total % 11
            return digits[-1] == check
        else:
            return super()._check_rx_id()
