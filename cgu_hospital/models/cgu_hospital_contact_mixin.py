from odoo import models, fields, api, _


class CGUHospitalContactMixin(models.AbstractModel):
    _name = 'cgu_hospital.contact.mixin'
    _description = 'Contact mixin'

    name = fields.Char(string='Full name')
    # readonly = True

    LastName = fields.Char(string='Last Name')
    FirstName = fields.Char(string='First Name')
    Surname = fields.Char(string='Surname')

    phone = fields.Char(string='phone')
    email = fields.Char(string='email')
    photo = fields.Image("Image 128", max_width=128, max_height=128, store=True)
    sex = fields.Selection(
        selection=[
            ('man', _('man')),
            ('woman', _('woman'))],
        string='Sex',
        default='man')

    @api.onchange('LastName', 'FirstName', 'Surname')
    def _onchange_name(self):
        self.name = "%s %s %s" % (self.LastName, self.FirstName, self.Surname)
