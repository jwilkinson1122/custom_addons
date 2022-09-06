from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Practice(models.Model):
    _name = "pod.practice"
    # _inherits = {
    #     'res.partner': 'partner_id',
    # }
    _inherit = "res.company"

    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
                                 help='Partner-related data of the Practice')
    is_practice = fields.Boolean()
    practice_name = fields.Char(
        string='Practice Name', required=True, tracking=True)

    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')
    active = fields.Boolean(string="Active", default=True)

    def open_practice_prescriptions(self):
        for records in self:
            return {
                'name': _('Practice Prescription'),
                'view_type': 'form',
                'domain': [('company_id', '=', records.id)],
                'res_model': 'company_id.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_practice': self.id},
                'type': 'ir.actions.act_window',
            }

    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('practice_name'):
            default['practice_name'] = _("%s (Copy)", self.practice_name)
        default['note'] = "Copied Record"
        return super(Practice, self).copy(default)

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['dr.prescription'].search_count(
                [('practice_id', '=', rec.id)])
            rec.prescription_count = prescription_count

    city_id = fields.Many2one(
        "res.city",
        compute="_compute_address",
        inverse="_inverse_city_id",
        string="City ID",
    )
    zip_id = fields.Many2one(
        "res.city.zip",
        string="ZIP Location",
        compute="_compute_address",
        inverse="_inverse_zip_id",
        help="Use the city name or the zip code to search the location",
    )
    country_enforce_cities = fields.Boolean(
        related="partner_id.country_id.enforce_cities"
    )

    def _get_company_address_field_names(self):
        """Add to the list of field to populate in _compute_address the new
        ZIP field + the city that is not handled at company level in
        `base_address_city`.
        """
        res = super()._get_company_address_field_names()
        res += ["city_id", "zip_id"]
        return res

    def _inverse_city_id(self):
        for company in self.with_context(skip_check_zip=True):
            company.partner_id.city_id = company.city_id

    def _inverse_zip_id(self):
        for company in self.with_context(skip_check_zip=True):
            company.partner_id.zip_id = company.zip_id

    def _inverse_state(self):
        self = self.with_context(skip_check_zip=True)
        return super(Practice, self)._inverse_state()

    def _inverse_country(self):
        self = self.with_context(skip_check_zip=True)
        return super(Practice, self)._inverse_country()

    @api.onchange("zip_id")
    def _onchange_zip_id(self):
        if self.zip_id:
            self.update(
                {
                    "zip": self.zip_id.name,
                    "city_id": self.zip_id.city_id,
                    "city": self.zip_id.city_id.name,
                    "country_id": self.zip_id.city_id.country_id,
                    "state_id": self.zip_id.city_id.state_id,
                }
            )

    @api.onchange("state_id")
    def _onchange_state_id(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id.id
