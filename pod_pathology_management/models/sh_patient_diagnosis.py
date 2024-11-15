# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, api


class Request_line(models.Model):
    _name = "sh.patho.request.line"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Appointment Line Detail"

    user_id = fields.Many2one(
        'res.users', required=False, default=lambda self: self.env.user)
    name = fields.Char(readonly=True)
    patho_request_id = fields.Many2one(
        'sh.patho.request', ondelete='cascade', string="Request")
    product_id = fields.Many2one('product.product', ondelete='cascade',
                                 copy=True, index=True, string="Product", required=True, tracking=True)
    desc = fields.Text(string="Description")
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.user.company_id.currency_id)
    price = fields.Float(string="Price")
    tax_ids = fields.Many2many('account.tax', string="Tax")
    subtotal = fields.Monetary(
        compute="_subtotal_compute", readonly=True, store=True, string="Subtotal")
    price_tax = fields.Float(compute='_subtotal_compute',
                             string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(
        compute='_subtotal_compute', string='Total', readonly=True, store=True)
    state_type = fields.Selection([('draft', 'Draft'), ('sample_received', 'Sample Received'), (
        'processing', 'Processing'), ('done', 'Done')], default="draft", string="Status", tracking=True)
    # lab_technician_id = fields.Many2one('res.partner', string="Lab Technician", ondelete='cascade')
    collection_center_id = fields.Many2one(
        'sh.collection.center', string="Collection Center", related="patho_request_id.collection_center_id", ondelete='cascade')
    laboratory_center_id = fields.Many2one(
        'sh.lab.center', string="Laboratory Center", related="patho_request_id.lab_center_id", ondelete='cascade')
    test_parameters_line = fields.One2many(
        'sh.lab.test.parameter.patient', 'request_line_id', string="Parameter Name", copy=True, auto_join=True)
    report_description = fields.Html(string="Report Description")
    patient_details_id = fields.Many2one(
        'res.partner', string="Patient", related="patho_request_id.patient_id", ondelete='cascade')
    technician_id = fields.Many2one('res.partner', string="Technician",)
    appointment_date = fields.Datetime(
        related="patho_request_id.appointment_date", string="Appointment")
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company)
    # test_description=fields.Text()

    def _compute_access_url(self):
        super(Request_line, self)._compute_access_url()
        for line in self:
            line.access_url = '/my/diagnosis/%s' % (line.id)

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'diagnosis.entry')
        res_ids = super(Request_line, self).create(vals_list)

        for res in res_ids:
            list_test_parameter = []
            res.test_parameters_line.unlink()
            if res.product_id and res.product_id.sh_patho_test_parameter_ids:
                for test_parameter in res.product_id.sh_patho_test_parameter_ids:
                    dic_test_parameter = {
                        'name': test_parameter.name,
                        'sequence': test_parameter.sequence,
                        'min_value': test_parameter.min_value,
                        'max_value': test_parameter.max_value,
                        'normal_value': test_parameter.normal_value,
                        'unit_id': test_parameter.unit_id.id
                    }
                    list_test_parameter.append((0, 0, dic_test_parameter))
            res.update({
                'test_parameters_line': list_test_parameter
            })
        return res_ids

    def write(self, vals):
        if vals.get("test_parameters_line", False) or vals.get('state_type'):
            return super(Request_line, self).write(vals)

        for rec in self:
            list_test_parameter = []
            rec.test_parameters_line.unlink()
            if vals.get('product_id'):
                product_id_obj = self.env['product.product'].browse(
                    vals.get('product_id'))

                if product_id_obj and product_id_obj.sh_patho_test_parameter_ids:
                    for test_parameter in product_id_obj.sh_patho_test_parameter_ids:
                        dic_test_parameter = {
                            'name': test_parameter.name,
                            'sequence': test_parameter.sequence,
                            'min_value': test_parameter.min_value,
                            'max_value': test_parameter.max_value,
                            'normal_value': test_parameter.normal_value,
                            'unit_id': test_parameter.unit_id.id
                        }
                        list_test_parameter.append((0, 0, dic_test_parameter))

            else:
                if rec.product_id and rec.product_id.sh_patho_test_parameter_ids:
                    for test_parameter in rec.product_id.sh_patho_test_parameter_ids:
                        dic_test_parameter = {
                            'name': test_parameter.name,
                            'sequence': test_parameter.sequence,
                            'min_value': test_parameter.min_value,
                            'max_value': test_parameter.max_value,
                            'normal_value': test_parameter.normal_value,
                            'unit_id': test_parameter.unit_id.id
                        }
                        list_test_parameter.append((0, 0, dic_test_parameter))

        vals.update({
            'test_parameters_line': list_test_parameter
        })

        res = super(Request_line, self).write(vals)

        return res

    @api.onchange('product_id')
    def _onchange_request_line(self):
        # Assignment of price Starts
        self.price = self.product_id.lst_price
        # Assignment of Tax starts
        product_id_tax_ids = self.product_id.taxes_id
        self.tax_ids = [(6, 0, product_id_tax_ids.ids)]
        # Assignment of description starts
        product_id_description = self.product_id.description_sale
        self.desc = product_id_description

    @api.depends('price', 'tax_ids')
    def _subtotal_compute(self):

        for line in self:
            price = line.price
            taxes = line.tax_ids.compute_all(price, line.currency_id, 1.0,
                                             product=line.product_id, partner=line.patho_request_id.patient_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'subtotal': taxes['total_excluded'],
            })
