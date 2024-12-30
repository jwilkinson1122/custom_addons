from odoo import models, fields, api, _


class SaleReportOrder(models.TransientModel):
    _name = "sale.report.wizard"
    _description = "Wizard for generate booking order"

    from_date = fields.Datetime(default=lambda self: fields.Datetime.now())
    to_date = fields.Datetime(default=lambda self: fields.Datetime.now())

    def print_excel(self):
        from_date = self.from_date
        to_date = self.to_date

        data = {
            "from_date": from_date,
            "to_date": to_date
        }

        self.env.ref('final_exam_hashmicro.action_sale_order_report_xlsx').sudo().report_file = "Sale Order Booking"

        action = self.env.ref('final_exam_hashmicro.action_sale_order_report_xlsx').report_action(self, data=data)
        action.update({'close_on_report_download': True})

        return action
