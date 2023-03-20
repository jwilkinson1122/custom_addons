# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.exceptions import Warning
# classes under  menu of laboratry


class podiatry_patient_rx(models.Model):
    _name = 'podiatry.patient.rx'
    _description = 'podiatry patient rx'
    _rec_name = 'podiatry_rx_type_id'

    request = fields.Char('Request', readonly=True)
    date = fields.Datetime('Date', default=fields.Datetime.now)
    rx_owner_partner_id = fields.Many2one('res.partner', 'Owner Name')
    urgent = fields.Boolean('Urgent',)
    owner_partner_id = fields.Many2one('res.partner')
    state = fields.Selection([('draft', 'Draft'), ('tested', 'Tested'),
                             ('cancel', 'Cancel')], readonly=True, default='draft')
    podiatry_rx_type_id = fields.Many2one(
        'podiatry.rx_type', 'Test Type', required=True)
    patient_id = fields.Many2one('podiatry.patient', 'Patient')
    doctor_id = fields.Many2one(
        'podiatry.practitioner', 'Practitioner', required=True)
    ship_to_patient = fields.Boolean('Ship to Patient')
    rx_res_created = fields.Boolean(default=False)
    is_invoiced = fields.Boolean(copy=False, default=False)

    @api.model
    def create(self, vals):
        vals['request'] = self.env['ir.sequence'].next_by_code('rx_seq')
        result = super(podiatry_patient_rx, self).create(vals)
        return result

    def cancel_rx(self):
        self.write({'state': 'cancel'})

    def create_rx(self):
        res_ids = []
        for browse_record in self:
            result = {}
            podiatry_rx_obj = self.env['podiatry.rx']
            res = podiatry_rx_obj.create({
                'name': self.env['ir.sequence'].next_by_code('pod_rx_seq'),
                'patient_id': browse_record.patient_id.id,
                'date_requested': browse_record.date or False,
                'rx_id': browse_record.podiatry_rx_type_id.id or False,
                'requestor_practitioner_id': browse_record.doctor_id.id or False,
            })
            res_ids.append(res.id)
            if res_ids:
                imd = self.env['ir.model.data']
                action = self.env.ref('pod_hms.action_podiatry_rx_form')
                list_view_id = imd.sudo()._xmlid_to_res_id('pod_hms.podiatry_rx_tree_view')
                form_view_id = imd.sudo()._xmlid_to_res_id('pod_hms.podiatry_rx_form_view')
                result = {
                    'name': action.name,
                    'help': action.help,
                    'type': action.type,
                    'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
                    'target': action.target,
                    'context': action.context,
                    'res_model': action.res_model,
                    'res_id': res.id,

                }

            if res_ids:
                result['domain'] = "[('id','=',%s)]" % res_ids

        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
