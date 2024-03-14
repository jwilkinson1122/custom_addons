# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, api
from datetime import date


class ShResPartner(models.Model):
    _inherit = 'res.partner'

    sh_patho_gender_type = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string="Gender")
    sh_patho_birthdate = fields.Date(string="Birth Date")
    sh_patho_age = fields.Integer(compute="_compute_age", string="Age")
    sh_patho_is_patient = fields.Boolean(string="Is Patient?")
    sh_patho_is_pathologist = fields.Boolean(string="Is Pathologist?")
    sh_patho_is_technician = fields.Boolean(string="Is Technician?")
    sh_patho_total_tests = fields.Integer(compute="get_total_tests")

    @api.depends('sh_patho_birthdate')
    def _compute_age(self):
        for rec in self:
            if rec.sh_patho_birthdate:
                days_in_year = 365.2425
                cal_age = int(
                    (date.today() - rec.sh_patho_birthdate).days / days_in_year)
                rec.sh_patho_age = cal_age
            else:
                rec.sh_patho_age = False

    def get_total_tests(self):
        for rec in self:
            lines = self.env['sh.patho.request.line'].search(
                [('patient_details_id.name', '=', rec.name)])
            total_tests = len(lines.ids)
            self.sh_patho_total_tests = total_tests

    def def_open_tests(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Products',
            'view_mode': 'tree,form',
            'res_model': 'sh.patho.request.line',
            'domain': [('patient_details_id.name', '=', self.name)],
        }

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ShResPartner, self).create(vals_list)
        for rec in res:
            if rec.sh_patho_is_technician:
                rec.env['res.users'].sudo().create({
                    'login': rec.email,
                    'name': rec.name,
                    'partner_id': rec.id,
                    'groups_id': [(4, self.env.ref('sh_pathology_management.sh_pathology_technician').id), (4, self.env.ref('base.group_user').id)]
                })
            elif rec.sh_patho_is_pathologist:
                rec.env['res.users'].sudo().create({
                    'login': rec.email,
                    'name': rec.name,
                    'partner_id': rec.id,
                    'groups_id': [(4, self.env.ref('sh_pathology_management.sh_pathology_pathologist').id), (4, self.env.ref('base.group_user').id), (4, self.env.ref('base.group_partner_manager').id)]
                })
        return res

    def write(self, vals):
        res = super(ShResPartner, self).write(vals)
        for rec in self:
            rs = rec.env['res.users'].search([('partner_id', '=', rec.id)])
            if rs and not rs.env.context.get('flag'):
                rs.with_context(flag=True).sudo().write({
                    # 'login': rec.email,
                    'name': rec.name,
                })
        return res


class ShResUsers(models.Model):
    _inherit = 'res.users'
