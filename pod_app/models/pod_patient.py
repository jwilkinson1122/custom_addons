from odoo import fields, models
from odoo.exceptions import ValidationError


class Patient(models.Model):
    """
    Describes a Patient catalogue.
    """
    _name = "pod.patient"
    _description = "Patient"

    name = fields.Char("Title", required=True)
    isbn = fields.Char("ISBN")
    active = fields.Boolean("Active?", default=True)
    date_published = fields.Date()
    image = fields.Binary("Cover")
    image2 = fields.Binary("Cover2")
    publisher_id = fields.Many2one("res.partner", string="Publisher")
    author_ids = fields.Many2many("res.partner", string="Authors")

    def _check_isbn(self):
        self.ensure_one()
        digits = [int(x) for x in self.isbn if x.isdigit()]
        if len(digits) == 13:
            ponderations = [1, 3] * 6
            terms = [a * b for a, b in zip(digits[:12], ponderations)]
            remain = sum(terms) % 10
            check = 10 - remain if remain != 0 else 0
            return digits[-1] == check

    def button_check_isbn(self):
        for patient in self:
            if not patient.isbn:
                raise ValidationError(
                    "Please provide an ISBN for %s" % patient.name)
            if patient.isbn and not patient._check_isbn():
                raise ValidationError("%s ISBN is invalid" % patient.isbn)
        return True