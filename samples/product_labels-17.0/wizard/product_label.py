# -*- coding: utf-8 -*-
from email.policy import default

from docutils.languages.uk import labels

from odoo import models, fields, api

from odoo.exceptions import UserError


class PrintProductLabel(models.TransientModel):
    _name = 'print.product.label'
    _description = 'Custom print product label'
    _inherit = 'mail.thread'

    name = fields.Char(string='Print Product Label')
    # Loop on action reports template names
    format_ids = fields.Many2one(
        string="Format",
        comodel_name='ir.actions.report',
        domain=[('model','=','print.product.label.lines')],
    )

    product_ids = fields.Many2one(comodel_name='product.template')


    @api.model
    def _get_product_label_ids(self):
        res = []
        """
            1. active_model is the technical name of the model
            2. active_id is the ID of the form active record or the tree view's 
               first record.
            3. active_ids is a list that contains the selected records or just one
               element.
            4. active_domain if the action is triggered from a form view
        """
        products = self.env[self._context.get('active_model')].browse(
            self._context.get('default_product_template_ids')
        )
        print(products)


    def get_labels_to_print(self):
        self.ensure_one()
        labels= ['apple']
        return labels

    def _get_report_action_params(self):
        self.ensure_one()
        return self.get_labels_to_print(), None

    def _prepare_report(self):
        output_mode = self._context.get('print_mode', 'pdf')
        # get ID action report
        if not self.format_ids:
            raise UserError('Please select a format type.')
        report = self.format_ids.with_context()
        report.sudo().write({'report_type': f'qweb-{output_mode}'})
        return report

    def action_print(self):
        report = self._prepare_report()
        return report.report_action(*self._get_report_action_params())