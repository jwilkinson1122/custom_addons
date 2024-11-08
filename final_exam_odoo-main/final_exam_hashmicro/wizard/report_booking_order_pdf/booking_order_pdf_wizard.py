from odoo import models, fields, api


class WizardBookingOrderPdf(models.TransientModel):
    _name = 'booking.report.wizardpdf'
    _description = 'Wizard Booking Order PDF'

    from_date = fields.Date(default=lambda self: fields.Datetime.now())
    to_date = fields.Date(default=lambda self: fields.Datetime.now())

    def action_print_report(self):
        report = []
        from_date = self.from_date
        to_date = self.to_date
        if from_date:
            report += [('date_order', '>=', from_date)]
        if to_date:
            report += [('date_order', '<=', to_date)]
        report += [('is_booking', '=', True)]

        final_report = self.env['sale.order'].search(report)

        report_data = []
        for order in final_report:
            for line in order.order_line:
                report_data.append({
                    'partner_id': order.partner_id.name,
                    'product_name': line.product_id.name,
                    'product_qty': line.product_uom_qty,
                    'qty_booking': line.qty_booking,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                    'taxes': ', '.join(line.tax_id.mapped('name')) if line.tax_id else 'N/A',
                    'amount_total': order.amount_total,
                    'write_date': order.write_date,
                })
        data = {
            'form': self.read()[0],
            'the_report': report_data,
        }

        report_action = self.env.ref('final_exam_hashmicro.report_sale_order_booking_order_pdf').report_action(self, data=data)
        report_action['close_on_report_download'] = True
        return report_action
