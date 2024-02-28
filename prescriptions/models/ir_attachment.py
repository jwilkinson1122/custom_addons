# -*- coding: utf-8 -*-

import base64
import io

from odoo import models, api
from PyPDF2 import PdfFileWriter, PdfFileReader


class IrAttachment(models.Model):
    _inherit = ['ir.attachment']

    @api.model
    def _pdf_split(self, new_files=None, open_files=None):
        """Creates and returns new pdf attachments based on existing data.

        :param new_files: the array that represents the new pdf structure:
            [{
                'name': 'New File Name',
                'new_pages': [{
                    'old_file_index': 7,
                    'old_page_number': 5,
                }],
            }]
        :param open_files: array of open file objects.
        :returns: the new PDF attachments
        """
        vals_list = []
        pdf_from_files = [PdfFileReader(open_file, strict=False) for open_file in open_files]
        for new_file in new_files:
            output = PdfFileWriter()
            for page in new_file['new_pages']:
                input_pdf = pdf_from_files[int(page['old_file_index'])]
                page_index = page['old_page_number'] - 1
                output.addPage(input_pdf.getPage(page_index))
            with io.BytesIO() as stream:
                output.write(stream)
                vals_list.append({
                    'name': new_file['name'] + ".pdf",
                    'datas': base64.b64encode(stream.getvalue()),
                })
        return self.create(vals_list)

    def _create_prescription(self, vals):
        """
        Implemented by bridge modules that create new prescriptions if attachments are linked to
        their business models.

        :param vals: the create/write dictionary of ir attachment
        :return True if new prescriptions are created
        """
        # Special case for prescriptions
        if vals.get('res_model') == 'prescriptions.prescription' and vals.get('res_id'):
            prescription = self.env['prescriptions.prescription'].browse(vals['res_id'])
            if prescription.exists() and not prescription.attachment_id:
                prescription.attachment_id = self[0].id
            return False

        # Generic case for all other models
        res_model = vals.get('res_model')
        res_id = vals.get('res_id')
        model = self.env.get(res_model)
        if model is not None and res_id and issubclass(type(model), self.pool['prescriptions.mixin']):
            vals_list = [
                model.browse(res_id)._get_prescription_vals(attachment)
                for attachment in self
                if not attachment.res_field
            ]
            vals_list = [vals for vals in vals_list if vals]  # Remove empty values
            self.env['prescriptions.prescription'].create(vals_list)
            return True
        return False

    @api.model_create_multi
    def create(self, vals_list):
        attachments = super().create(vals_list)
        for attachment, vals in zip(attachments, vals_list):
            # the context can indicate that this new attachment is created from prescriptions, and therefore
            # doesn't need a new prescription to contain it.
            if not self._context.get('no_prescription') and not attachment.res_field:
                attachment.sudo()._create_prescription(dict(vals, res_model=attachment.res_model, res_id=attachment.res_id))
        return attachments

    def write(self, vals):
        if not self._context.get('no_prescription'):
            self.filtered(lambda a: not (vals.get('res_field') or a.res_field)).sudo()._create_prescription(vals)
        return super(IrAttachment, self).write(vals)
