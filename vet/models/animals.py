from odoo import models, fields, api
from odoo.exceptions import UserError


class Animal(models.Model):
    _name = "animal"
    _description = "Animals table"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order ="identification desc"

    name = fields.Char(string="Name", required=True)
    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string="Sex", default="male")
    birthdate = fields.Date(string="Birthdate")
    photo = fields.Binary(string="Photo")
    breed = fields.Many2one("animal.breed", string="Breed")
    species = fields.Many2one("animal.specie", string="Specie", required=True)
    owner = fields.Many2one('res.partner', string="Owner", store=True)
    weight = fields.Float(string="Weight")
    height = fields.Float(string="Height")
    size = fields.Selection([
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ], string="Size", default='small')
    medicines = fields.Many2many("animal.medicine", string="Medicines", relation="animal_medicine_rel")
    vaccines = fields.Many2many("animal.vaccine", string="Vaccines", relation="animal_vaccine_rel")
    diseases = fields.Many2many("animal.disease", string="Diseases", relation="animal_disease_rel")
    allergies = fields.Many2many("animal.allergy", string="Allergies", relation="animal_allergy_rel")
    surgeries = fields.Many2many("animal.surgery", string="Surgeries", relation="animal_surgery_rel")
    visit_ids = fields.One2many('animal.visit', 'animal_id', string='Visits')
    active = fields.Boolean(string="Active", default=True)
    tags = fields.Many2many("animal.tag", string="Tags", relation="animal_tag_rel")
    insurance = fields.Many2one("animal.insurance", string="Insurance", relation="animal_insurance_rel")
    identification = fields.Char(string="ID", required=True, copy=False, readonly=True, index=True, default=lambda self: 'New')
    internal_notes = fields.Text(string="Notes")
    quote_count = fields.Integer(string="Quotes", compute="_compute_quote_count")
    invoice_count = fields.Integer(string="Invoices", compute="_compute_invoice_count")
    visit_count = fields.Integer(string="Visits", compute="_compute_visit_count")



    @api.model
    def create(self, vals):
        if vals.get('identification', 'New') == 'New':
            vals['identification'] = self.env['ir.sequence'].next_by_code('animal.identification') or 'New'
        return super(Animal, self).create(vals)

    @api.depends('owner')
    def _compute_quote_count(self):
        for record in self:
            if record.owner:
                record.quote_count = self.env['sale.order'].search_count([('partner_id', '=', record.owner.id)])
            else:
                record.quote_count = 0

    @api.depends('owner')
    def _compute_invoice_count(self):
        for record in self:
            if record.owner:
                record.invoice_count = self.env['account.move'].search_count([('partner_id', '=', record.owner.id)])
            else:
                record.invoice_count = 0

    @api.depends('owner')
    def _compute_visit_count(self):
        for record in self:
            if record.id:
                record.visit_count = self.env['animal.visit'].search_count([('animal_id', '=', record.id)])
            else:
                record.visit_count = 0

    def action_view_quotes(self):
        # Obtener el ID del partner asociado
        partner_id = self.owner.id

        return {
            'name': 'Quotes',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('partner_id', '=', partner_id)],
            'context': dict(self._context),
        }

    def action_view_invoices(self):
        # Obtener el ID del partner asociado
        partner_id = self.owner.id

        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('partner_id', '=', partner_id)],
            'context': dict(self._context),
        }

    def action_view_visits(self):
        # Obtener el ID del partner asociado
        animal = self.id

        return {
            'name': 'Visits',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'animal.visit',
            'domain': [('animal_id', '=', animal)],
            'context': dict(self._context),
        }

    def action_create_quote(self):
        # Asegurarse de que el animal tiene un dueño
        if not self.owner:
            raise UserError('This animal does not have an owner defined.')

        return {
            'type': 'ir.actions.act_window',
            'name': 'New Quote',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_partner_id': self.owner.id,  # Prellenar el cliente con el dueño del animal
            },
        }
