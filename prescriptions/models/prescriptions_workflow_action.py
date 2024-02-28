# -*- coding: utf-8 -*-


from odoo import fields, models


class WorkflowTagAction(models.Model):
    _name = "prescriptions.workflow.action"
    _description = "Prescription Workflow Tag Action"

    workflow_rule_id = fields.Many2one('prescriptions.workflow.rule', ondelete='cascade')

    action = fields.Selection([
        ('add', "Add"),
        ('replace', "Replace by"),
        ('remove', "Remove"),
    ], default='add', required=True)

    facet_id = fields.Many2one('prescriptions.facet', string="Category")
    tag_id = fields.Many2one('prescriptions.tag', string="Tag")

    def execute_tag_action(self, prescription):
        if self.action == 'add' and self.tag_id.id:
            return prescription.write({'tag_ids': [(4, self.tag_id.id, False)]})
        elif self.action == 'replace' and self.facet_id.id:
            faceted_tags = self.env['prescriptions.tag'].search([('facet_id', '=', self.facet_id.id)])
            if faceted_tags.ids:
                for tag in faceted_tags:
                    prescription.write({'tag_ids': [(3, tag.id, False)]})
            if self.tag_id:
                return prescription.write({'tag_ids': [(4, self.tag_id.id, False)]})
        elif self.action == 'remove':
            if self.tag_id.id:
                return prescription.write({'tag_ids': [(3, self.tag_id.id, False)]})
            elif self.facet_id:
                faceted_tags = self.env['prescriptions.tag'].search([('facet_id', '=', self.facet_id.id)])
                for tag in faceted_tags:
                    return prescription.write({'tag_ids': [(3, tag.id, False)]})
