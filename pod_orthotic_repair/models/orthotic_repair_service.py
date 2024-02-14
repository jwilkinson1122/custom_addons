# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RepairTeam(models.Model):
    """Repair Team"""
    _name = 'repair.team'
    _description = __doc__
    _rec_name = 'title'

    color = fields.Integer()
    title = fields.Char(string="Title", required=True, translate=True)
    responsible_id = fields.Many2one('res.users', default=lambda self: self.env.user, string="Responsible",
                                     required=True)
    team_member_ids = fields.Many2many('res.users', string="Team Members")
    project_id = fields.Many2one('project.project', readonly=True, store=True, string="Project")

    @api.model
    def default_get(self, fields):
        record = super(RepairTeam, self).default_get(fields)
        if self.env.ref('pod_orthotic_repair.orthotic_repair_project'):
            record['project_id'] = self.env.ref('pod_orthotic_repair.orthotic_repair_project').id
        else:
            rec = self.env['project.project'].sudo().create({
                'name': 'Orthotic Repair Project',
                'user_id': self.env.user.id,
                'company_id': self.env.company.id,
            })
            record['project_id'] = rec.id
        return record


class OrthoticRepairService(models.Model):
    """Orthotic Repair Service"""
    _name = 'orthotic.repair.service'
    _description = __doc__
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Service", domain=[('is_repair_service', '=', True)],
                                 required=True)
    description = fields.Char(string="Description", translate=True, required=True)
    service_charge = fields.Monetary(string="Service Charge")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    orthotic_repair_order_id = fields.Many2one('orthotic.repair.order')

    @api.onchange('product_id')
    def get_orthotic_service_charge(self):
        for rec in self:
            if rec.product_id:
                rec.service_charge = rec.product_id.lst_price


class RepairService(models.Model):
    """Repair Service"""
    _name = 'repair.service'
    _description = __doc__
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Service", domain=[('is_repair_service', '=', True)],
                                 required=True)
    description = fields.Char(string="Description", translate=True)
    project_task_id = fields.Many2one('project.task')
