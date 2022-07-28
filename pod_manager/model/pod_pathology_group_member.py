# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class pod_pathology_group_member(models.Model):
    _name = 'pod.pathology.group.member'
    _description = 'podiatry pathology group member'

    condition_group_id = fields.Many2one(
        'pod.pathology.group', string="Group", required=True)
