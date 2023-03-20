# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime
# classes under  menu of laboratry


class podiatry_rx_create(models.TransientModel):
    _name = 'podiatry.rx.create'
    _description = 'podiatry rx create'

    def create_rx(self):
        res_ids = []
        rx_rqu_obj = self.env['podiatry.patient.rx']
        browse_records = rx_rqu_obj.browse(self._context.get('active_ids'))
        result = {}
        for browse_record in browse_records:
            podiatry_rx_obj = self.env['podiatry.rx']
            res = podiatry_rx_obj.create({'name': self.env['ir.sequence'].next_by_code('pod_rx_seq'),
                                          'patient_id': browse_record.patient_id.id or False,
                                          'date_requested': browse_record.date or False,
                                          'rx_id': browse_record.podiatry_rx_type_id.id or False,
                                          'requestor_practitioner_id': browse_record.doctor_id.id or False,
                                          })
            res_ids.append(res.id)
            if res_ids:
                imd = self.env['ir.model.data']
                write_ids = rx_rqu_obj.browse(self._context.get('active_id'))
                write_ids.write({'state': 'tested'})
                action = self.env.ref('pod_hms.action_podiatry_rx_tree')
                list_view_id = imd._xmlid_to_res_id(
                    'pod_hms.podiatry_rx_tree_view')
                form_view_id = imd._xmlid_to_res_id(
                    'pod_hms.podiatry_rx_form_view')
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
