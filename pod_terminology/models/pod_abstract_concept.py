
from odoo import api, fields, models
from odoo.osv import expression


class PodAbstractConcept(models.AbstractModel):

    _name = "pod.abstract.concept"
    _description = "Podiatry abstract concept"

    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    definition = fields.Char()
    editable = fields.Boolean(default=True)

    @api.depends("name", "code")
    def name_get(self):
        result = []
        for record in self:
            name = "[%s]" % record.code
            if record.name:
                name = "{} {}".format(name, record.name)
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                "|",
                ("code", "=ilike", name + "%"),
                ("name", operator, name),
            ]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ["&", "!"] + domain[1:]
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()
