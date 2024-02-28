# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class WorkflowActionRuleProduct(models.Model):
    _inherit = ['prescriptions.workflow.rule']

    create_model = fields.Selection(selection_add=[('product.template', "Product template")])

    def create_record(self, prescriptions=None):
        rv = super(WorkflowActionRuleProduct, self).create_record(prescriptions=prescriptions)
        if self.create_model == 'product.template':
            product = self.env[self.create_model].create({'name': 'product created from Prescriptions'})
            image_is_set = False

            for prescription in prescriptions:
                # this_prescription is the prescription in use for the workflow
                this_prescription = prescription
                if (prescription.res_model or prescription.res_id) and prescription.res_model != 'prescriptions.prescription':
                    attachment_copy = prescription.attachment_id.with_context(no_prescription=True).copy()
                    this_prescription = prescription.copy({'attachment_id': attachment_copy.id})
                this_prescription.write({
                    'res_model': product._name,
                    'res_id': product.id,
                })
                if 'image' in this_prescription.mimetype and not image_is_set:
                    product.write({'image_1920': this_prescription.datas})
                    image_is_set = True

            view_id = product.get_formview_id()
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.template',
                'name': "New product template",
                'context': self._context,
                'view_mode': 'form',
                'views': [(view_id, "form")],
                'res_id': product.id if product else False,
                'view_id': view_id,
            }
        return rv
