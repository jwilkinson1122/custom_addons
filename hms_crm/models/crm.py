from odoo import  models,fields,api


class crm(models.Model):
    _inherit="res.partner"

    related_patient_id=fields.Text()
    namexxx=fields.Text()