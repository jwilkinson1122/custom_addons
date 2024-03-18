


from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pod_pos_order_number = fields.Boolean(
        string="Display Order Number")
    pod_pos_receipt_bacode_qr = fields.Boolean(
        string="Display Barcode / QrCode")
    pod_pos_receipt_barcode_qr_selection = fields.Selection(
        [('barcode', 'Barcode'), ('qr', 'QrCode')], default='barcode')
    pod_pos_receipt_invoice = fields.Boolean(string="Display Invoice Number")
    pod_pos_receipt_customer_detail = fields.Boolean(
        string="Display Customer Detail")
    pod_pos_receipt_customer_name = fields.Boolean(
        string="Display Customer Name")
    pod_pos_receipt_customer_address = fields.Boolean(
        string="Display Customer Address")
    pod_pos_receipt_customer_mobile = fields.Boolean(
        string="Display Customer Mobile")
    pod_pos_receipt_customer_phone = fields.Boolean(
        string="Display Customer Phone")
    pod_pos_receipt_customer_email = fields.Boolean(
        string="Display Customer Email")
    pod_pos_vat = fields.Boolean(string="Display Customer Vat")
    pod_pos_vat_name = fields.Char(string='vat name')
    pod_enable_a3_receipt = fields.Boolean(string="Use A3 receipts")
    pod_enable_a4_receipt = fields.Boolean(string="Use A4 receipts")
    pod_enable_a5_receipt = fields.Boolean(string="Use A5 receipts")
    pod_default_receipt = fields.Selection([
        ('a3_size','A3 Size'),
        ('a4_size','A4 Size'),
        ('a5_size','A5 Size'),
    ],string="Standard Receipts")
