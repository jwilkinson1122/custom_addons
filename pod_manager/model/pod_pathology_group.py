# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class pod_pathology_group(models.Model):
    _name = 'pod.pathology.group'
    _description = 'podiatry pathology group'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    desc = fields.Char(string="Short Description", required=True)
    info = fields.Text(string="Detailed Information")
