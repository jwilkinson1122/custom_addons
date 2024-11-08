from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import pytz
import locale

locale.setlocale(locale.LC_ALL, '')


class PaymentReport(models.AbstractModel):
    _name = 'report.final_exam_hashmicro.action_sale_order_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Model for generating excel report"

    def generate_xlsx_report(self, workbook, data, periode):
        from_date = data["from_date"]
        to_date = data["to_date"]
        worksheet = self.create_worksheet(workbook)
        worksheet = self.generate_header(workbook, worksheet, from_date, to_date)
        worksheet = self.generate_data(workbook, worksheet, from_date, to_date)
        self.set_width_columns(worksheet)

    def create_worksheet(self, workbook):
        # Create worksheet
        worksheet = workbook.add_worksheet('Sale Order Report')

        return worksheet

    def generate_header(self, workbook, worksheet, from_date, to_date):
        # Formats
        title_format = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_name': 'Calibri',
            'font_size': 16,
            'valign': 'vcenter'
        })

        sub_title_format = workbook.add_format({
            'align': 'center',
            'bold': True,
            'valign': 'vcenter'
        })

        header_format = workbook.add_format({
            "align": "center",
            "bold": True,
            "valign": "vcenter",
            "text_wrap": True
        })

        # generate title
        worksheet.merge_range("A1:N1", "Sale Order Report", title_format)

        # periode
        if from_date and to_date:
            user_tz = self.env.user.tz or pytz.utc
            local = pytz.timezone(user_tz)

            from_date_str = datetime.strptime(str(from_date), DEFAULT_SERVER_DATETIME_FORMAT).astimezone(local)
            to_date_str = datetime.strptime(str(to_date), DEFAULT_SERVER_DATETIME_FORMAT).astimezone(local)
            periode = "PERIODE: " + from_date_str.strftime('%d/%m/%Y %H:%M') + " s/d. " + to_date_str.strftime(
                '%d/%m/%Y %H:%M')

            worksheet.merge_range("A2:N2", f"{periode}", sub_title_format)

        # Generate header
        headers = ["Nomor SO", "Tanggal Jual", "Jam", "Nomor Jual", "Nomor Terima", "Customer", "Jumlah",
                   "Uang Diterima", "Jenis Bayar", "Status Bayar", "Level",
                   "Tangal Void", "Status"]

        unicode = 65
        for header in headers:
            range_cell = f"{chr(unicode)}4:{chr(unicode)}5"
            worksheet.merge_range(range_cell, header, header_format)
            unicode += 1

        return worksheet

    def generate_data(self, workbook, worksheet, from_date, to_date):
        centering_format = workbook.add_format({"align": "center"})
        right_format = workbook.add_format({"align": "right"})

        if from_date and to_date:
            sale_obj = self.env["sale.order"].search([
                ("create_date", ">=", from_date),
                ("create_date", "<=", to_date),
            ], order='create_date asc')
        else:
            sale_obj = self.env["data.upload"].search([], order='create_date asc')

        if not sale_obj:
            raise ValidationError(_("The data is empty, please check the parameters you entered."))

        row, col = 5, 0
        for i, data in enumerate(sale_obj):
            # invoices
            inv = None
            rinv = None
            for invoice in data.invoice_ids:
                if 'refund' in invoice.move_type:
                    rinv = invoice
                else:
                    inv = invoice

                #Nomor SO
                worksheet.write(row, col, data.name or None)

                # Tanggal Jual
                worksheet.write(row, col + 1, data.create_date.strftime('%d/%m/%Y') or None, centering_format)

                #jam
                worksheet.write(row, col, + 2, data.create_date.strftime('%H:%M') or None, centering_format)

                # Customer
                worksheet.write(row, col + 6, data.partner_id.display_name or None)

                # Jumlah
                worksheet.write(row, col + 7, data.amount_total, right_format or None)

                # Uang Diterima
                worksheet.write(row, col + 8, data.payment_id.payment_received or None, right_format)

                # Jenis Bayar
                worksheet.write(row, col + 9, data.payment_method.name or None, centering_format)

                #status Bayar
                if inv:
                    status = 'Paid Off'
                    if inv.payment_state == 'not_paid':
                        status = 'Unpaid'
                    elif inv.payment_state == 'partial':
                        status = 'DP'
                else:
                    status = 'Unpaid'

                worksheet.write(row, col + 10, status or None, centering_format)
                # Level
                worksheet.write(row, col + 11, 1, centering_format)

                # Tangal Void
                worksheet.write(row, col + 12, rinv.create_date.strftime('%d/%m/%Y %H:%M') if rinv else None,
                                centering_format)

                # Status
                cust_type = 'Company'
                if data.partner_id.company_type == 'person':
                    cust_type = 'Individual'

                worksheet.write(row, col + 13, cust_type or None)

                row += 1

            return worksheet

    @staticmethod
    def set_width_columns(worksheet):
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 25)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 10)
        worksheet.set_column('M:M', 20)
        worksheet.set_column('N:N', 15)
        worksheet.set_column('O:O', 10)