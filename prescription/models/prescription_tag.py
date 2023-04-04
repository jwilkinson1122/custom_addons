# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import api, fields, models


class PrescriptionTagCategory(models.Model):
    _name = "prescription.tag.category"
    _description = "Prescription Tag Category"
    _order = "sequence"

    name = fields.Char("Name", required=True, translate=True)
    sequence = fields.Integer('Sequence', default=0)
    tag_ids = fields.One2many('prescription.tag', 'category_id', string="Tags")

class PrescriptionTag(models.Model):
    _name = "prescription.tag"
    _description = "Prescription Tag"
    _order = "sequence"

    def _default_color(self):
        return randint(1, 11)

    name = fields.Char("Name", required=True, translate=True)
    sequence = fields.Integer('Sequence', default=0)
    category_id = fields.Many2one("prescription.tag.category", string="Category", required=True, ondelete='cascade')
    color = fields.Integer(
        string='Color Index', default=lambda self: self._default_color(),
        help='Tag color. No color means no display in kanban or front-end, to distinguish internal tags from public categorization tags.')
