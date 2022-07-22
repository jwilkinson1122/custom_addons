from odoo import fields, models
from odoo.exceptions import ValidationError


class Prescription(models.Model):
    """
    Describes a Prescription archive.
    """
    _name = "clinic.prescription"
    _description = "Prescription"

    name = fields.Char("Title", required=True)
    rx_id = fields.Char("RxID")
    active = fields.Boolean("Active?", default=True)
    date_administered = fields.Date(string="Date")
    image = fields.Binary("Cover")
    administrator_id = fields.Many2one("res.partner", string="Administrator")
    doctor_ids = fields.Many2many("res.partner", string="Doctors")

    def _check_rx_id(self):
        self.ensure_one()
        digits = [int(x) for x in self.rx_id if x.isdigit()]
        if len(digits) == 13:
            ponderations = [1, 3] * 6
            terms = [a * b for a, b in zip(digits[:12], ponderations)]
            remain = sum(terms) % 10
            check = 10 - remain if remain != 0 else 0
            return digits[-1] == check

    def button_check_rx_id(self):
        for prescription in self:
            if not prescription.rx_id:
                raise ValidationError(
                    "Please provide an RxID for %s" % prescription.name)
            if prescription.rx_id and not prescription._check_rx_id():
                raise ValidationError("%s RxID is invalid" %
                                      prescription.rx_id)
        return True
