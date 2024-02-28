# -*- coding: utf-8 -*-


from odoo import models, fields, api


class Tags(models.Model):
    _name = "prescriptions.tag"
    _description = "Tag"
    _order = "sequence, name"

    folder_id = fields.Many2one('prescriptions.folder', string="Workspace", related='facet_id.folder_id', store=True,
                                readonly=False)
    facet_id = fields.Many2one('prescriptions.facet', string="Category", ondelete='cascade', required=True)
    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)

    _sql_constraints = [
        ('facet_name_unique', 'unique (facet_id, name)', "Tag already exists for this facet"),
    ]

    @api.depends('facet_id')
    @api.depends_context('simple_name')
    def _compute_display_name(self):
        if self._context.get('simple_name'):
            return super()._compute_display_name()
        for record in self:
            record.display_name = f"{record.facet_id.name} > {record.name}"

    @api.model
    def _get_tags(self, domain, folder_id):
        """
        fetches the tag and facet ids for the prescription selector (custom left sidebar of the kanban view)
        """
        prescriptions = self.env['prescriptions.prescription'].search(domain)
        # folders are searched with sudo() so we fetch the tags and facets from all the folder hierarchy (as tags
        # and facets are inherited from ancestor folders).
        folders = self.env['prescriptions.folder'].sudo().search([('parent_folder_id', 'parent_of', folder_id)])
        self.flush_model(['sequence', 'name', 'facet_id'])
        self.env['prescriptions.facet'].flush_model(['sequence', 'name', 'tooltip'])
        query = """
            SELECT  facet.sequence AS group_sequence,
                    facet.id AS group_id,
                    facet.tooltip AS group_tooltip,
                    prescriptions_tag.sequence AS sequence,
                    prescriptions_tag.id AS id,
                    COUNT(rel.prescriptions_prescription_id) AS __count
            FROM prescriptions_tag
                JOIN prescriptions_facet facet ON prescriptions_tag.facet_id = facet.id
                    AND facet.folder_id = ANY(%s)
                LEFT JOIN prescription_tag_rel rel ON prescriptions_tag.id = rel.prescriptions_tag_id
                    AND rel.prescriptions_prescription_id = ANY(%s)
            GROUP BY facet.sequence, facet.name, facet.id, facet.tooltip, prescriptions_tag.sequence, prescriptions_tag.name, prescriptions_tag.id
            ORDER BY facet.sequence, facet.name, facet.id, facet.tooltip, prescriptions_tag.sequence, prescriptions_tag.name, prescriptions_tag.id
        """
        params = [
            list(folders.ids),
            list(prescriptions.ids),  # using Postgresql's ANY() with a list to prevent empty list of prescriptions
        ]
        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()

        # Translating result
        groups = self.env['prescriptions.facet'].browse({r['group_id'] for r in result})
        group_names = {group['id']: group['name'] for group in groups}

        tags = self.env['prescriptions.tag'].browse({r['id'] for r in result})
        tags_names = {tag['id']: tag['name'] for tag in tags}

        for r in result:
            r['group_name'] = group_names.get(r['group_id'])
            r['display_name'] = tags_names.get(r['id'])

        return result
