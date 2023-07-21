from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

class InheritedResPartner(models.Model):
    _inherit = 'res.partner'
    
    # force "active_test" domain to bypass _search() override
    child_ids = fields.One2many(
        domain=[("active", "=", True), ("is_company", "=", False)]
    )

    # force "active_test" domain to bypass _search() override
    affiliate_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Affiliates",
        domain=[("active", "=", True), ("is_company", "=", True)],
    )
    
    # type = fields.Selection(selection_add=[('main_address', 'Main Address'), ('contact')])
    # address_type = fields.Selection(
    #      ('invoice', 'Invoice Address'),
    #      ('delivery', 'Shipping Address'), 
    #     string='Address Type',
    #     default='invoice',
    #     help="Invoice & Delivery addresses are used in sales orders.")

    fax = fields.Char()
    dob = fields.Date()
    age = fields.Integer(compute='_cal_age',store=True,readonly=True)
    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_customer_prescriptions(self):
        for records in self:
            return {
                'name':_('Prescription History'),
                'view_type': 'form',
                'domain': [('customer', '=',records.id)],
                'res_model': 'dr.prescription',
                'view_id': False,
                'view_mode':'tree,form',
                'context':{'default_customer':self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['dr.prescription'].search_count([('customer','=',records.id)])
            records.prescription_count = count

    @api.depends('dob')
    def _cal_age(self):
        for record in self:
            if record.dob:
                years = relativedelta(date.today(), record.dob).years
                record.age = str(int(years))
            else:
                record.age = 0
                
    @api.constrains("ref", "is_company", "company_id")
    def _check_ref(self):
        for partner in self.filtered("ref"):
            # If the company is not defined in the partner, take current user company
            company = partner.company_id or self.env.company
            mode = company.partner_ref_unique
            # Don't raise when coming from contact merge wizard or no duplicates
            if not self.env.context.get("partner_ref_unique_merging") and (
                mode == "all" or (mode == "companies" and partner.is_company)
            ):
                domain = [
                    ("id", "!=", partner.id),
                    ("ref", "=", partner.ref),
                ]
                if mode == "companies":
                    domain.append(("is_company", "=", True))
                other = self.search(domain)
                if other:
                    raise ValidationError(
                        _("This reference is equal to partner '%s'")
                        % other[0].display_name
                    )














