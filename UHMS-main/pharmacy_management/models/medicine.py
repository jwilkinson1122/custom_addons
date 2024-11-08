from odoo import models, fields, api
from odoo.exceptions import UserError

class Medicine(models.Model):
    _name = 'pharmacy.medicine'
    _description = 'Medicine'

    name = fields.Char(string='Name', required=True)
    category = fields.Many2one('product.category', string='Category')
    stock = fields.Float(string='Stock Quantity', required=True)
    quantity_available = fields.Integer(string='Quantity Available', required=True, default=0)
    price = fields.Float(string='Price', required=True)
    prescription_required = fields.Boolean(string='Prescription Required', default=False)

    @api.model
    def check_stock_levels(self):
        low_stock_medicines = self.search([('quantity_available', '<=', 10)])
        if low_stock_medicines:
            template = self.env.ref('pharmacy_management.email_template_low_stock')
            for medicine in low_stock_medicines:
                template.send_mail(medicine.id, force_send=True)

















# from odoo import models, fields

# class Medicine(models.Model):
#     _name = 'pharmacy.medicine'
#     _description = 'Medicine'

#     name = fields.Char(string='Medicine Name', required=True)
#     description = fields.Text(string='Description')
#     code = fields.Char(string='Medicine Code', required=True, unique=True)
#     category = fields.Selection([
#         ('tablet', 'Tablet'),
#         ('syrup', 'Syrup'),
#         ('injection', 'Injection'),
#         ('ointment', 'Ointment'),
#     ], string='Category', required=True)
#     price = fields.Float(string='Price', required=True)
#     stock_level = fields.Integer(string='Stock Level', compute='_compute_stock_level', store=True)
#     quantity_available = fields.Integer(string='Quantity Available', required=True)
#     expiration_date = fields.Date(string='Expiration Date')
#     supplier_id = fields.Many2one('res.partner', string='Supplier')
#     prescription_ids = fields.One2many('pharmacy.prescription', 'medicine_id', string='Prescriptions')

#     # Smart buttons
#     prescription_count = fields.Integer(compute='_compute_prescription_count')

#     def _compute_prescription_count(self):
#         for record in self:
#             record.prescription_count = len(record.prescription_ids)

#     @api.depends('quantity_available')
#     def _compute_stock_level(self):
#         for medicine in self:
#             if medicine.quantity_available > 50:
#                 medicine.stock_level = 'Sufficient'
#             elif 10 < medicine.quantity_available <= 50:
#                 medicine.stock_level = 'Low'
#             else:
#                 medicine.stock_level = 'Critical'

#     def action_view_prescriptions(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Prescriptions',
#             'view_mode': 'tree,form',
#             'res_model': 'pharmacy.prescription',
#             'domain': [('medicine_id', '=', self.id)],
#         }

#     @api.model
#     def check_stock_levels(self):
#         low_stock_medicines = self.search([('quantity_available', '<=', 10)])
#         if low_stock_medicines:
#             template = self.env.ref('pharmacy_management.email_template_low_stock')
#             for medicine in low_stock_medicines:
#                 template.send_mail(medicine.id, force_send=True)