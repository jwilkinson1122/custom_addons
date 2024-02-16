

from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_helpdesk = fields.Boolean("Helpdesk Ticket?")
    helpdesk_team = fields.Many2one('helpdesk.team', string='Helpdesk Team')
    helpdesk_assigned_to = fields.Many2one('res.users', string='Assigned to')
    available_in_pos = fields.Boolean(string='Available in POS', help='Check if you want this product to appear in the Point of Sale.', default=False)

    prescription_ok = fields.Boolean(default=True, string="Can be Configured")
    
    description_prescription = fields.Text(
        'Prescription Description', translate=True,
        help="A description of the Product that you want to communicate to your customers. "
             "This description will be copied to every Prescription Order")

    service_type = fields.Selection(
        selection=[('manual', "Manually set quantities on order")],
        string="Track Service",
        compute='_compute_service_type', store=True, readonly=False, precompute=True,
        help="Manually set quantities on order: Invoice based on the manually entered quantity, without creating an analytic account.\n"
             "Timesheets on contract: Invoice based on the tracked hours on the related timesheet.\n"
             "Create a task and track hours: Create a task on the prescription order validation and track the work hours.")
    prescription_line_warn = fields.Selection(
        WARNING_MESSAGE, string="Prescription Order Line",
        help=WARNING_HELP, required=True, default="no-message")
    prescription_line_warn_msg = fields.Text(string="Message for Prescription Order Line")
    expense_policy = fields.Selection(
        selection=[
            ('no', "No"),
            ('cost', "At cost"),
            ('prescription_price', "Prescription price"),
        ],
        string="Re-Invoice Expenses", default='no',
        compute='_compute_expense_policy', store=True, readonly=False,
        help="Validated expenses and vendor bills can be re-invoiced to a customer at its cost or prescription price.")
    visible_expense_policy = fields.Boolean(
        string="Re-Invoice Policy visible", compute='_compute_visible_expense_policy')
    prescription_count = fields.Float(
        string="Sold", compute='_compute_prescription_count', digits='Product Unit of Measure')
    invoice_policy = fields.Selection(
        selection=[
            ('order', "Ordered quantities"),
            ('delivery', "Delivered quantities"),
        ],
        string="Invoicing Policy",
        compute='_compute_invoice_policy', store=True, readonly=False, precompute=True,
        help="Ordered Quantity: Invoice quantities ordered by the customer.\n"
             "Delivered Quantity: Invoice quantities delivered to the customer.")

    @api.depends('name')
    def _compute_visible_expense_policy(self):
        visibility = self.user_has_groups('analytic.group_analytic_accounting')
        for product_template in self:
            product_template.visible_expense_policy = visibility

    @api.depends('prescription_ok')
    def _compute_expense_policy(self):
        self.filtered(lambda t: not t.prescription_ok).expense_policy = 'no'

    @api.depends('product_variant_ids.prescription_count')
    def _compute_prescription_count(self):
        for product in self:
            product.prescription_count = float_round(sum([p.prescription_count for p in product.with_context(active_test=False).product_variant_ids]), precision_rounding=product.uom_id.rounding)

    @api.constrains('company_id')
    def _check_prescription_product_company(self):
        """Ensure the product is not being restricted to a single company while
        having been sold in another one in the past, as this could cause issues."""
        target_company = self.company_id
        if target_company:  # don't prevent writing `False`, should always work
            subquery_products = self.env['product.product'].sudo().with_context(active_test=False)._search([('product_tmpl_id', 'in', self.ids)])
            rx_lines = self.env['prescription.order.line'].sudo().search_read(
                [('product_id', 'in', subquery_products), '!', ('company_id', 'child_of', target_company.root_id.id)],
                fields=['id', 'product_id'],
            )
            used_products = list(map(lambda rxl: rxl['product_id'][1], rx_lines))
            if rx_lines:
                raise ValidationError(_('The following products cannot be restricted to the company'
                                        ' %s because they have already been used in quotations or '
                                        'prescription orders in another company:\n%s\n'
                                        'You can archive these products and recreate them '
                                        'with your company restriction instead, or leave them as '
                                        'shared product.', target_company.name, ', '.join(used_products)))

    def action_view_prescription(self):
        action = self.env['ir.actions.actions']._for_xml_id('pod_prescription.report_all_channels_prescription_action')
        action['domain'] = [('product_tmpl_id', 'in', self.ids)]
        action['context'] = {
            'pivot_measures': ['product_uom_qty'],
            'active_id': self._context.get('active_id'),
            'active_model': 'prescription.report',
            'search_default_Prescription': 1,
            'search_default_filter_order_date': 1,
        }
        return action

    @api.onchange('type')
    def _onchange_type(self):
        res = super(ProductTemplate, self)._onchange_type()
        if self._origin and self.prescription_count > 0:
            res['warning'] = {
                'title': _("Warning"),
                'message': _("You cannot change the product's type because it is already used in prescription orders.")
            }
        return res

    @api.depends('type')
    def _compute_service_type(self):
        self.filtered(lambda t: t.type == 'consu' or not t.service_type).service_type = 'manual'

    @api.depends('type')
    def _compute_invoice_policy(self):
        self.filtered(lambda t: t.type == 'consu' or not t.invoice_policy).invoice_policy = 'order'

    @api.model
    def get_import_templates(self):
        res = super(ProductTemplate, self).get_import_templates()
        if self.env.context.get('prescription_multi_pricelist_product_template'):
            # return [{
            #         'label': _("Import Template for Products"),
            #         'template': '/product/static/xls/product_template.xls'
            #     }]
            if self.user_has_groups('product.group_prescription_pricelist'):
                return [{
                    'label': _("Import Template for Products"),
                    'template': '/product/static/xls/product_template.xls'
                }]
        return res

    @api.model
    def create(self, vals):
        templates = super (ProductTemplate,self).create(vals)
        if templates.product_variant_count<= 1:
            if templates.product_variant_id:
                templates.product_variant_id.is_helpdesk = templates.is_helpdesk
                templates.product_variant_id.helpdesk_team = templates.helpdesk_team.id
                templates.product_variant_id.helpdesk_assigned_to = templates.helpdesk_assigned_to.id
        return templates

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if not self.product_variant_count > 1:
            if self.product_variant_id:
                self.product_variant_id.is_helpdesk = self.is_helpdesk
                self.product_variant_id.helpdesk_team = self.helpdesk_team
                self.product_variant_id.helpdesk_assigned_to = self.helpdesk_assigned_to
        else:
            if self.product_variant_id:
                self.product_variant_id.is_helpdesk = False
                self.product_variant_id.helpdesk_team.unlink()
                self.product_variant_id.helpdesk_assigned_to.unlink()

        return res
 