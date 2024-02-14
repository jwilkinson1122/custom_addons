# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InspectionImage(models.Model):
    """Inspection Image"""
    _name = "inspection.image"
    _description = __doc__
    _rec_name = 'name'

    avatar = fields.Binary(string="Avatar")
    name = fields.Char(string="Name", required=True, translate=True)
    orthotic_repair_order_id = fields.Many2one('orthotic.repair.order')


class OrthoticRepairOrder(models.Model):
    """Orthotic Repair Order"""
    _name = 'orthotic.repair.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'sequence_number'

    sequence_number = fields.Char(string='Sequence No', readonly=True, default=lambda self: _('New'), copy=False)
    orthotic_problem = fields.Char(string="Problem", required=True, translate=True)
    orthotic_product_id = fields.Many2one('product.product', domain=[('is_orthotic', '=', True)], string="Orthotic",
                                         required=True)
    model = fields.Char(string="Model", translate=True)
    mfg_year = fields.Char(string="MFG Year", translate=True)
    orthotic_brand = fields.Char(string="Brand", translate=True)
    serial_number = fields.Char(string="Serial Number", translate=True)

    is_previous_service_history = fields.Boolean(string="Previous Service History")
    customer_id = fields.Many2one('res.partner', string='Customer')
    phone = fields.Char(string="Phone", translate=True)
    email = fields.Char(string="Email", translate=True)
    street = fields.Char(string="Street", translate=True)
    street2 = fields.Char(string="Street 2", translate=True)
    city = fields.Char(string="City", translate=True)
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country")
    zip = fields.Char(string="Zip")

    receiving_date = fields.Date(string="Receiving Date", default=fields.date.today())
    delivery_date = fields.Date(string="Delivery Date")
    problem_description = fields.Text(string="Problem Descriptions", translate=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    company_phone = fields.Char(related="company_id.phone", translate=True, string=" Phone")
    company_email = fields.Char(related="company_id.email", translate=True, string=" Email")

    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    responsible_id = fields.Many2one('res.users', default=lambda self: self.env.user, string="Responsible",
                                     required=True)
    supervisor_id = fields.Many2one('res.users', string="Supervisor")

    team_id = fields.Many2one('repair.team', string="Team")
    technician_id = fields.Many2one('res.users', string="Technician")
    team_project_id = fields.Many2one(related="team_id.project_id", string="Project")
    team_task_id = fields.Many2one('project.task', readonly=True, store=True, string="Repair Diagnosis")

    previous_service_history_ids = fields.One2many('previous.service.history', 'orthotic_repair_order_id',
                                                   string="Previous")
    material_of_repair_ids = fields.One2many('material.of.repair', 'orthotic_repair_order_id',
                                             string="Required Parts")
    orthotic_repair_service_ids = fields.One2many('orthotic.repair.service', 'orthotic_repair_order_id',
                                                 string="Orthotic Repair Services")
    inspection_image_ids = fields.One2many('inspection.image', 'orthotic_repair_order_id', string="Images")
    is_website_order = fields.Boolean(string="Website Repair Order")
    work_is_done = fields.Boolean(related="team_task_id.work_is_done", string="Work is Done")
    task_count = fields.Integer(compute="_get_task_count", string="Count")

    total_part_price = fields.Monetary(string="Part Price", compute="_total_part_price", store=True)
    total_service_charge = fields.Monetary(string="Service Charge", compute="_total_service_charge", store=True)
    total = fields.Monetary(string="Total", readonly=True, store=True, compute="_get_total_charge")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    state = fields.Selection(related="sale_order_id.state")
    order_amount = fields.Monetary(related='sale_order_id.amount_total', string="Total Amount")

    delivery_order_count = fields.Integer(compute="_get_delivery_order_count", string="Delivery Orders")
    sale_invoiced = fields.Monetary()
    invoice_id = fields.Many2one('account.move')

    date = fields.Date(string="Date")
    signature = fields.Binary(string="Authorized Signature")
    file_name = fields.Char(string="File Name", translate=True)
    attachment = fields.Binary(string="File Attachment")

    analysis_template_id = fields.Many2one('analysis.template', string="Analysis Template")
    required_analysis_ids = fields.One2many('required.analysis', 'orthotic_repair_order_id',
                                            string="Required Diagnosis")
    diagnosed_problem_ids = fields.One2many('diagnosed.problem', 'orthotic_repair_order_id', string="Diagnosed Problems")
    reject_reason = fields.Text(string="Quotation Reject Reasons")
    stages = fields.Selection(
        [('draft', "New"), ('assign_to_technician', "Assign to Technician"), ('inspection_mode', "Inspection Mode"),
         ('quotation', "Quotation"), ('quotation_sent', "Quotation Sent"), ('approve', "Quotation Approved"),
         ('reject', "Reject"), ('in_progress', "In Progress"), ('review', "Review"), ('complete', "Complete"),
         ('cancel', "Cancel")], default='draft', string="Stages", group_expand='_expand_groups')

    check_list_template_id = fields.Many2one('checklist.template', string="Checklist Template")
    repair_checklist_ids = fields.One2many('repair.checklist', 'orthotic_repair_order_id', string="Checklist")
    sale_order_count = fields.Integer(compute="_get_sale_order_count", string="Sale Orders")
    priority = fields.Selection([('0', 'Normal'), ('1', 'Low'), ('2', 'High'), ('3', 'Very High')], string="Priority",
                                default='0')

    @api.model
    def _expand_groups(self, states, domain, order):
        return ['draft', 'assign_to_technician', 'inspection_mode', 'quotation', 'quotation_sent', 'approve', 'reject',
                'in_progress', 'review', 'complete', 'cancel']

    def assign_to_technician_to_inspection_mode(self):
        self.stages = 'inspection_mode'

    def inspection_mode_to_quotation(self):
        total = self.total_part_price + self.total_service_charge
        if not self.total > 0:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'message': "Please add the required parts and services.",
                    'sticky': False,
                }
            }
            return message
        self.stages = 'quotation'
        order_line = []
        for record in self.material_of_repair_ids:
            quotation_record = {
                'product_id': record.product_id.id,
                'name': record.product_id.name,
                'product_uom_qty': record.product_qty,
                'product_uom': record.uom_id.id,
                'price_unit': record.price,
            }
            order_line.append((0, 0, quotation_record)),
        if self.total_service_charge > 0.0:
            for data in self.orthotic_repair_service_ids:
                service_data = {
                    'product_id': data.product_id.id,
                    'name': data.description,
                    'price_unit': data.service_charge,
                }
                order_line.append((0, 0, service_data))
        data = {
            'partner_id': self.customer_id.id,
            'date_order': fields.Datetime.now(),
            'order_line': order_line,
            'orthotic_repair_order_id': self.id,
        }
        if total > 0:
            sale_order_id = self.env['sale.order'].sudo().create(data)
            self.sale_order_id = sale_order_id.id
            amount_total = sale_order_id.amount_total
            self.sale_invoiced = amount_total
            return {
                'type': 'ir.actions.act_window',
                'name': _('Sale Order'),
                'res_model': 'sale.order',
                'res_id': sale_order_id.id,
                'view_mode': 'form',
                'target': 'current'
            }

    def quotation_sent_to_approve(self):
        self.stages = 'approve'

    def quotation_to_reject(self):
        self.stages = 'reject'

    def reject_to_inspection_mode(self):
        self.stages = 'inspection_mode'

    def in_progress_to_review(self):
        self.stages = 'review'

    def review_to_complete(self):
        self.ensure_one()
        template_id = self.env.ref("pod_orthotic_repair.orthotic_repair_mail_template").sudo()
        ctx = {
            'default_model': 'orthotic.repair.order',
            'default_res_ids': self.ids,
            'default_partner_ids': [self.customer_id.id],
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
            'default_email_from': self.env.company.email,
            'default_reply_to': self.env.company.email,
            'custom_layout': False,
            'force_email': True,
        }
        self.stages = 'complete'
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def complete_to_cancel(self):
        self.stages = 'cancel'

    @api.onchange('customer_id')
    def customer_details(self):
        for rec in self:
            if rec.customer_id:
                rec.phone = rec.customer_id.phone
                rec.email = rec.customer_id.email

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence_number', _('New')) == _('New'):
                vals['sequence_number'] = self.env['ir.sequence'].next_by_code('orthotic.repair.order') or _('New')
        res = super(OrthoticRepairOrder, self).create(vals_list)
        return res

    def create_repair_order(self):
        if not self.supervisor_id:
            message = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': "Please Select Supervisor first !",
                    'sticky': False,
                }
            }
            return message
        data = {
            'name': self.orthotic_problem,
            'project_id': self.team_project_id.id,
            'partner_id': self.customer_id.id,
            'user_ids': self.technician_id.ids,
            'orthotic_repair_order_id': self.id
        }
        team_task_id = self.env['project.task'].create(data)
        for problem in self.diagnosed_problem_ids:
            problem = {
                'description': problem.problem_name,
                'project_task_id': team_task_id.id,
            }
            self.env['task.orthotic.problem'].create(problem)
        self.team_task_id = team_task_id.id
        self.stages = 'in_progress'
        return {
            'type': 'ir.actions.act_window',
            'name': _('Repair Task'),
            'res_model': 'project.task',
            'res_id': team_task_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def _get_delivery_order_count(self):
        for rec in self:
            delivery_order_count = self.env['stock.picking'].search_count([('origin', '=', self.sale_order_id.name)])
            rec.delivery_order_count = delivery_order_count

    def action_delivery_orders_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delivery Orders'),
            'res_model': 'stock.picking',
            'domain': [('origin', '=', self.sale_order_id.name)],
            'view_mode': 'tree,form,kanban',
            'target': 'current'
        }

    def action_sale_order_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def _get_task_count(self):
        for rec in self:
            task_count = self.env['project.task'].search_count([('orthotic_repair_order_id', '=', rec.id)])
            rec.task_count = task_count

    def action_task_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Repair Task'),
            'res_model': 'project.task',
            'res_id': self.team_task_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    @api.depends('material_of_repair_ids.price', 'material_of_repair_ids.product_qty')
    def _total_part_price(self):
        for rec in self:
            total_part_price = 0.0
            for part in rec.material_of_repair_ids:
                total_part_price = total_part_price + (part.price * part.product_qty)
            rec.total_part_price = total_part_price

    @api.depends('orthotic_repair_service_ids')
    def _total_service_charge(self):
        for rec in self:
            total_service_charge = 0.0
            for service in rec.orthotic_repair_service_ids:
                total_service_charge = total_service_charge + service.service_charge
            rec.total_service_charge = total_service_charge

    @api.depends('total_part_price', 'total_service_charge')
    def _get_total_charge(self):
        for rec in self:
            rec.total = rec.total_part_price + rec.total_service_charge

    @api.onchange('analysis_template_id')
    def get_analysis_template_items(self):
        for rec in self:
            if rec.analysis_template_id:
                checklist_items = []
                for item in rec.analysis_template_id.analysis_template_item_ids:
                    checklist_items.append((0, 0, {'description': item.name}))
                rec.required_analysis_ids = [(5, 0, 0)]
                rec.required_analysis_ids = checklist_items

    def unlink(self):
        for res in self:
            if res.stages != 'complete':
                res = super(OrthoticRepairOrder, res).unlink()
                return res
            else:
                raise ValidationError(_('You cannot delete the completed order.'))

    def draft_to_assign_to_technician(self):
        self.stages = 'assign_to_technician'

    def inspection_mode_to_in_progress(self):
        self.stages = 'in_progress'

    def action_create_repair_sale_order(self):
        total = self.total_part_price + self.total_service_charge
        order_line = []
        for record in self.material_of_repair_ids:
            quotation_record = {
                'product_id': record.product_id.id,
                'name': record.product_id.name,
                'product_uom_qty': record.product_qty,
                'product_uom': record.uom_id.id,
                'price_unit': record.price,
            }
            order_line.append((0, 0, quotation_record)),

        if self.total_service_charge > 0.0:
            service = ""
            for data in self.orthotic_repair_service_ids:
                service = service + "{} - {} {}, \n".format(data.product_id.name, self.currency_id.symbol,
                                                            data.service_charge)
            service_data = {
                'product_id': self.env.ref('pod_orthotic_repair.service_charge').id,
                'name': service,
                'price_unit': self.total_service_charge,
            }
            order_line.append((0, 0, service_data))
        data = {
            'partner_id': self.customer_id.id,
            'date_order': fields.Datetime.now(),
            'order_line': order_line,
            'orthotic_repair_order_id': self.id,
        }
        if total > 0:
            sale_order_id = self.env['sale.order'].sudo().create(data)
            self.sale_order_id = sale_order_id.id
            amount_total = sale_order_id.amount_total
            self.sale_invoiced = amount_total
            return {
                'type': 'ir.actions.act_window',
                'name': _('Sale Order'),
                'res_model': 'sale.order',
                'res_id': sale_order_id.id,
                'view_mode': 'form',
                'target': 'current'
            }
        message = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'danger',
                'message': "The value of a sale order cannot be zero.",
                'sticky': False,
            }
        }
        return message

    def _get_sale_order_count(self):
        for rec in self:
            sale_order_count = self.env['sale.order'].search_count([('orthotic_repair_order_id', '=', rec.id)])
            rec.sale_order_count = sale_order_count

    def get_services_and_parts(self):
        self.material_of_repair_ids = [(5, 0, 0)]
        for part in self.team_task_id.mro_quotation_ids:
            part = {
                'product_id': part.product_id.id,
                'serial_number': part.serial_number,
                'product_qty': part.qty,
                'uom_id': part.uom_id.id,
                'remarks': part.remarks,
                'orthotic_repair_order_id': part.project_task_id.orthotic_repair_order_id.id,
            }
            self.env['material.of.repair'].create(part)

        self.orthotic_repair_service_ids = [(5, 0, 0)]
        for service in self.team_task_id.repair_service_ids:
            service = {
                'product_id': service.product_id.id,
                'description': service.description,
                'orthotic_repair_order_id': service.project_task_id.orthotic_repair_order_id.id,
            }
            self.env['orthotic.repair.service'].create(service)

    @api.onchange('check_list_template_id')
    def get_checklist_items(self):
        for rec in self:
            if rec.check_list_template_id:
                checklist_items = []
                for item in rec.check_list_template_id.checklist_template_item_ids:
                    checklist_items.append((0, 0, {'name': item.name}))
                rec.repair_checklist_ids = [(5, 0, 0)]
                rec.repair_checklist_ids = checklist_items
