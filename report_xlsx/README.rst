================
Base report xlsx
================

This module provides a basic report class to generate xlsx report.

Installation
============

Make sure you have ``xlsxwriter`` Python module installed::

$ pip3 install xlsxwriter

For testing it is also necessary ``xlrd`` Python module installed::

$ pip3 install xlrd

Usage
=====

An example of XLSX report for partners on a module called `module_name`:

A python class ::

    from odoo import models

    class PartnerXlsx(models.AbstractModel):
        _name = 'report.module_name.report_name'
        _inherit = 'report.report_xlsx.abstract'

        def generate_xlsx_report(self, workbook, data, partners):
            for obj in partners:
                report_name = obj.name
                # One sheet by partner
                sheet = workbook.add_worksheet(report_name[:31])
                bold = workbook.add_format({'bold': True})
                sheet.write(0, 0, obj.name, bold)

To manipulate the ``workbook`` and ``sheet`` objects, refer to the
`documentation <http://xlsxwriter.readthedocs.org/>`_ of ``xlsxwriter``.

A report XML record ::

    <report
        id="partner_xlsx"
        model="res.partner"
        string="Print to XLSX"
        report_type="xlsx"
        name="module_name.report_name"
        file="res_partner"
        attachment_use="False"
    />
