from odoo import models, fields, api
import xlsxwriter
import base64
from io import BytesIO
from datetime import datetime


class SaleOrderReportWizard(models.TransientModel):
    _name = 'booking.order.report.wizard'
    _description = 'Sale Order Report Wizard'

    from_date = fields.Datetime(default=lambda self: fields.Datetime.now())
    to_date = fields.Datetime(default=lambda self: fields.Datetime.now())

    def action_print_report(self):
        # Filter records based on from_date, to_date and is_booking=True
        sale_orders = self.env['sale.order'].search([
            ('date_order', '>=', self.from_date),
            ('date_order', '<=', self.to_date),
            ('is_booking', '=', True)
        ])

        # Create a workbook and add a worksheet
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Add a bold format for the header
        bold = workbook.add_format({'bold': True})
        # Add a border format for the cells
        border = workbook.add_format({'border': 1})

        # Write the header row with bold format
        headers = ['Order ID', 'Product ID', 'Order Date', 'Customer', 'Total Amount', 'Status', 'Product', 'Quantity', 'Quantity Booking', 'Unit Price', 'Subtotal']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, bold)

        # Start from the first cell below the headers
        row = 1
        for order in sale_orders:
            order_date = order.date_order.strftime('%Y-%m-%d %H:%M:%S') if order.date_order else ''
            for line in order.order_line:
                worksheet.write(row, 0, order.name, border)
                worksheet.write(row, 1, line.product_id.id, border)
                worksheet.write(row, 2, order_date, border)
                worksheet.write(row, 3, order.partner_id.name, border)
                worksheet.write(row, 4, order.amount_total, border)
                worksheet.write(row, 5, order.state, border)
                worksheet.write(row, 6, line.product_id.name, border)
                worksheet.write(row, 7, line.product_uom_qty, border)
                worksheet.write(row, 8, line.qty_booking, border)
                worksheet.write(row, 9, line.price_unit, border)
                worksheet.write(row, 10, line.price_subtotal, border)
                row += 1

        workbook.close()
        output.seek(0)
        file_data = base64.b64encode(output.read())

        # Membuat attachment
        attachment = self.env['ir.attachment'].create({
            'name': 'Booking_Order_Report_Excel.xlsx',
            'type': 'binary',
            'datas': file_data,
            'store_fname': 'booking_order_report.xlsx',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % attachment.id,
                'target': 'self',
            }
