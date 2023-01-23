from odoo import models, fields, api, _


class ContactMixin(models.AbstractModel):
    _name = 'podiatry.contact.mixin'
    _description = 'Contact mixin'

    name = fields.Char(string='Full name')
    # readonly = True

    LastName = fields.Char(string='Last Name')
    FirstName = fields.Char(string='First Name')
    Surname = fields.Char(string='Surname')

    phone = fields.Char(string='phone')
    email = fields.Char(string='email')
    photo = fields.Image("Image 128", max_width=128,
                         max_height=128, store=True)
    gender = fields.Selection(
        selection=[
            ('male', _('Male')),
            ('female', _('Female'))],
        string='Gender',
        default='male')

    @api.onchange('LastName', 'FirstName', 'Surname')
    def _onchange_name(self):
        self.name = "%s %s %s" % (self.LastName, self.FirstName, self.Surname)