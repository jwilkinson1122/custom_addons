# -*- coding: utf-8 -*-
from odoo import models, fields, api



class TreatmentAction(models.Model):
    _name = 'treatment.action'
    _description = 'Tooth Treatment'
    _order = 'sequence'

    name = fields.Char('Name')
    color = fields.Char('Color') 
    checked = fields.Boolean('Checked', default=False)
    action = fields.Selection([('extraction','Extraction'),
                               ('coronne','Coronne'),
                               ('implant','Implant'),
                               ('missing','Missing'),
                               ('bridge','Bridge')
                               ])
    sequence = fields.Integer('Sequence')

    replace_tooth = fields.Boolean('Replace tooth')
    replace_racine = fields.Boolean('Replace racine')



    img_top_replace = fields.Binary('Img top replace')
    img_bottom_replace = fields.Binary('Img bottom replace')
    racine_bottom_replace = fields.Binary('Racine bottom replace')
    racine_top_replace = fields.Binary('Racine top replace')


    def return_treatment_action(self,ids):
        record_ids= self.browse(ids)
        for record in record_ids.sorted(key='sequence'):

            vals= {
                'id' : record.id,
                'replace_tooth': record.replace_tooth,
                'replace_racine': record.replace_racine,
                'img_top_replace':  "/web/image?model=treatment.action&id=%s&field=img_top_replace"% record.id,
                'img_bottom_replace': "/web/image?model=treatment.action&id=%s&field=img_bottom_replace"% record.id,
                'racine_bottom_replace': "/web/image?model=treatment.action&id=%s&field=racine_bottom_replace"% record.id,
                'racine_top_replace': "/web/image?model=treatment.action&id=%s&field=racine_top_replace"% record.id,
            }
            return vals

    
