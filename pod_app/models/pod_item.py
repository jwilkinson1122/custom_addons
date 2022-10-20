from odoo import fields, models
from odoo.exceptions import ValidationError


class Item(models.Model):
    """
    Describes a Item catalogue.
    """
    _name = "pod.item"
    _description = "Item"

    name = fields.Char("Title", required=True)
    isbn = fields.Char("ISBN")
    active = fields.Boolean("Active?", default=True)
    date_published = fields.Date()
    image = fields.Binary("Cover")
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
        for item in self:
            if not item.isbn:
                raise ValidationError(
                    "Please provide an ISBN for %s" % item.name)
            if item.isbn and not item._check_isbn():
                raise ValidationError("%s ISBN is invalid" % item.isbn)
        return True
