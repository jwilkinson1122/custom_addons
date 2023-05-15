from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models,_

class InheritedResPartner(models.Model):
    _inherit = 'res.partner'
    
 
    is_practitioner = fields.Boolean(string="Practitioner")
    is_practice = fields.Boolean('Practice')
    is_patient = fields.Boolean(string='Patient')

    
    # force "active_test" domain to bypass _search() override
    child_ids = fields.One2many(
        domain=[("active", "=", True), ("is_company", "=", False)]
    )

    # force "active_test" domain to bypass _search() override
    practice_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Practices",
        domain=[("active", "=", True), ("is_company", "=", True)],
    )
    
    prescription_count = fields.Integer(compute='get_prescription_count')

    def create_sale_order_prescriptions(self):
        for records in self:
            return {
                'name':_('Prescriptions'),
                'view_type': 'form',
                'domain': [('practice', '=',records.id)],
                'res_model': 'practitioner.prescription',
                'view_id': False,
                'view_mode':'tree,form',
                'context':{'default_practice':self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['practitioner.prescription'].search_count([('practice','=',records.id)])
            records.prescription_count = count

  














