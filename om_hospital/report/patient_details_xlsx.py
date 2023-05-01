import base64
import io

from odoo import models


class PatientXlsx(models.AbstractModel):
    _name = 'report.om_hospital.report_patient_details_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, patients):
        sheet = workbook.add_worksheet("Patient Card ID")
        # style
        bold = workbook.add_format({'bold': True})
        format_1 = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'yellow'})
        row = 2
        col = 2
        for obj in patients:
            report_name = obj.name
            # every patient in a single sheet
            # sheet = workbook.add_worksheet(report_name[:31])
            # to merge two column
            row += 1
            sheet.merge_range(row, col-1, row, col, "ID CARD", format_1)
            # title ID CARD without mege
            # row += 1
            # sheet.write(row, col, "ID CARD", bold)
            # add image
            row += 1
            if obj.image:
                patient_image = io.BytesIO(base64.b64decode(obj.image))
                sheet.insert_image(row, col, "image.png", {'image_data': patient_image, 'x_scale': 0.1, 'y_scale': 0.1})
            # line one name : patient name
            row += 1
            sheet.write(row, col-1, "Name: ", bold)
            sheet.write(row, col, obj.name)
            # line two age : patient age
            row += 1
            sheet.write(row, col-1, "Age: ", bold)
            sheet.write(row, col, obj.age)
            # line three responsible : patient responsible
            row += 1
            sheet.write(row, col-1, "Responsible: ", bold)
            sheet.write(row, col, obj.responsible_id.name)
            # space before next card
            row += 2

