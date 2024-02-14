# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class OrthoticProduct(models.Model):
    """Orthotic"""
    _inherit = 'product.product'
    _description = __doc__

    is_repair_service = fields.Boolean(string="Orthotic Repair Service")
    is_orthotic_part = fields.Boolean(string="Orthotic Part")
    is_orthotic = fields.Boolean(string="Orthotic")


class OrthoticProductTemplate(models.Model):
    """Orthotic"""
    _inherit = 'product.template'
    _description = __doc__

    is_repair_service = fields.Boolean(string="Orthotic Repair Service")
    is_orthotic_part = fields.Boolean(string="Orthotic Part")
    is_orthotic = fields.Boolean(string="Orthotic")


class SaleOrder(models.Model):
    """Sale Order"""
    _inherit = 'sale.order'
    _description = __doc__

    orthotic_repair_order_id = fields.Many2one('orthotic.repair.order', string="MRO")

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.orthotic_repair_order_id:
            res['orthotic_repair_order_id'] = self.orthotic_repair_order_id.id
        return res

    def action_quotation_send(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        self.ensure_one()
        self.order_line._validate_analytic_distribution()
        lang = self.env.context.get('lang')
        mail_template = self._find_mail_template()
        if mail_template and mail_template.lang:
            lang = mail_template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.order',
            'default_res_ids': self.ids,
            'default_template_id': mail_template.id if mail_template else None,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        if self.orthotic_repair_order_id:
            self.orthotic_repair_order_id.stages = 'quotation_sent'
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


class SaleInvoice(models.Model):
    """Sale Invoice"""
    _inherit = 'account.move'
    _description = __doc__

    orthotic_repair_order_id = fields.Many2one('orthotic.repair.order', string="MRO")


class ResPartners(models.Model):
    """Res Partners"""
    _inherit = 'res.partner'
    _description = __doc__

    mro_count = fields.Integer(compute="_get_mro_count", string="MRO")

    def _get_mro_count(self):
        for rec in self:
            mro = self.env['orthotic.repair.order'].search_count([('customer_id', '=', rec.id)])
            rec.mro_count = mro

    def action_mro_view(self):
        return {
            'name': _('Repair Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'orthotic.repair.order',
            'view_mode': 'kanban,tree,form',
            'domain': [('customer_id', '=', self.id)],
            'target': 'current',
        }


class ProjectTask(models.Model):
    """Project Task"""
    _inherit = 'project.task'
    _description = __doc__

    orthotic_repair_order_id = fields.Many2one('orthotic.repair.order', string="Orthotic Repair Order")
    task_orthotic_problem_ids = fields.One2many('task.orthotic.problem', 'project_task_id',
                                               string="Task Orthotic Problems")
    work_is_done = fields.Boolean(string="Work is Done")
    mro_count = fields.Integer(compute="_get_mro_count", string="Count")

    def _get_mro_count(self):
        for rec in self:
            mro_count = self.env['orthotic.repair.order'].search_count([('team_task_id', '=', rec.id)])
            rec.mro_count = mro_count

    def action_mro_view(self):
        return {
            'name': _('Repair Diagnosis'),
            'type': 'ir.actions.act_window',
            'res_model': 'orthotic.repair.order',
            'view_mode': 'form',
            'res_id': self.orthotic_repair_order_id.id,
            'target': 'current',
        }

    def work_is_completed(self):
        for rec in self.task_orthotic_problem_ids:
            if not rec.is_check:
                message = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'warning',
                        'message': "Please complete diagnosis problems",
                        'sticky': False,
                    }
                }
                return message
            self.work_is_done = True
