# -*- coding: utf-8 -*-


from random import randint

from odoo import api, fields, models


class PracticeTagCategory(models.Model):
    _name = "practice.tag.category"
    _description = "Practice Tag Category"
    _order = "sequence"

    name = fields.Char("Name", required=True, translate=True)
    sequence = fields.Integer('Sequence', default=0)
    tag_ids = fields.One2many('practice.tag', 'category_id', string="Tags")

class PracticeTag(models.Model):
    _name = "practice.tag"
    _description = "Practice Tag"
    _order = "sequence"

    def _default_color(self):
        return randint(1, 11)

    name = fields.Char("Name", required=True, translate=True)
    sequence = fields.Integer('Sequence', default=0)
    category_id = fields.Many2one("practice.tag.category", string="Category", required=True, ondelete='cascade')
    color = fields.Integer(
        string='Color Index', default=lambda self: self._default_color(),
        help='Tag color. No color means no display in kanban or front-end, to distinguish internal tags from public categorization tags.')
