from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = "res.partner"

    location_link = fields.Char()
    is_location = fields.Boolean('Is Location')

    # company_type = fields.Selection(selection_add=[('location', 'Location')])
    
    company_type = fields.Selection(string='Company Type',
        selection_add=[('location', 'Location')],
        compute='_compute_company_type', inverse='_write_company_type')

    # @api.depends('is_company')
    # def _compute_company_type(self):
    #     for partner in self:
    #         partner.company_type = 'company' if partner.is_company else 'person'
    
    @api.depends()
    def _compute_company_type(self):
        """OVERWRITE: Enable selection of other type."""
        for partner in self:
            if partner.is_company:
                partner.company_type = 'company'
            elif partner.is_location:
                partner.company_type = 'location' 
            else:
                partner.company_type = 'person'
                
    # def _write_company_type(self):
    #     for partner in self:
    #         partner.is_company = partner.company_type == 'company'

    def _write_company_type(self):
        for partner in self:
            partner.is_company = partner.company_type == 'company'
            partner.is_location = partner.company_type == 'location'

    # @api.onchange('company_type')
    # def onchange_company_type(self):
    #     self.is_company = (self.company_type == 'company')

    @api.onchange('company_type')
    def onchange_company_type(self):
        """OVERWRITE: Enable selection of other type."""
        self.is_location = (self.company_type == 'location')
        self.is_company = (self.company_type == 'company')