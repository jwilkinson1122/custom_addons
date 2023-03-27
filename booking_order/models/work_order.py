from odoo import fields, models, api, _


class WorkOrder(models.Model):
    _name = 'work.order'
    _description = 'Work Order'
    _rec_name = "wo_number"
    
    practice_id = fields.Many2one(comodel_name='practice.practice_id', string='Practice')
    
    practitioner_id = fields.Many2one(comodel_name='practitioner.practitioner_id', string='Practitioner')
   
    patient_id = fields.Many2one(comodel_name='patient.patient_id', string='Patient')
    
    bo_reference = fields.Many2one(comodel_name='sale.order', readonly=True)

    wo_number = fields.Char(
        string='WO Number',
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: _('New'))

    planned_start = fields.Datetime(
        string="Planned Start",
        required=True)
    planned_end = fields.Datetime(
        string='Planned End',
        required=True)
    date_start = fields.Datetime(
        string='Date Start',
        readonly=True)
    date_end = fields.Datetime(
        string='Date End',
        readonly=True)
    state = fields.Selection(
        [('pending', 'Pending'), ('in_progress', 'In Progress'), ('done', 'Done'), ('cancelled', 'Cancelled')],
        string='State',
        default='pending',
        track_visibility='onchange')
    note = fields.Text(
        string='Note')

    @api.model
    def create(self, vals):
        if vals.get('wo_number', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['wo_number'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'work.order') or _('New')
            else:
                vals['wo_number'] = self.env['ir.sequence'].next_by_code('work.order') or _('New')
        return super(WorkOrder, self).create(vals)

    def start_work(self):
        return self.write({'state': 'in_progress', 'date_start': fields.Datetime.now()})

    def end_work(self):
        return self.write({'state': 'done', 'date_end': fields.Datetime.now()})

    def reset(self):
        return self.write({'state': 'pending', 'date_start': ''})

    def cancel(self):
        return self.write({'state': 'cancelled'})
