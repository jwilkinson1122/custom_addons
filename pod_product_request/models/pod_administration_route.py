from odoo import fields, models


class PodiatryAdministrationRoute(models.Model):

    _name = "pod.administration.route"
    _description = "Podiatry Administration Route"

    name = fields.Char()
