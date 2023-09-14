# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = "product.template"

    commercial = fields.Char(index=True)

    @api.depends("commercial", "default_code", "name")
    def _compute_display_name(self):
        return super()._compute_display_name()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Include commercial name in direct name search."""
        args = expression.normalize_domain(args)
        for arg in args:
            if isinstance(arg, (list, tuple)):
                if arg[0] == "name" or arg[0] == "display_name":
                    index = args.index(arg)
                    args = (
                        args[:index]
                        + ["|", ("commercial", arg[1], arg[2])]
                        + args[index:]
                    )
                    break
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        """Give preference to commercial names on name search"""
        if not args:
            args = []
        recs = self.search([("commercial", operator, name)] + args, limit=limit)
        res = recs.name_get()
        if limit:
            limit_rest = limit - len(recs)
        else:  # pragma: no cover
            # limit can be 0 or None representing infinite
            limit_rest = limit
        if limit_rest or not limit:
            args += [("id", "not in", recs.ids)]
            res += super().name_search(
                name, args=args, operator=operator, limit=limit_rest
            )
        return res

    def name_get(self):
        result = []
        orig_name = dict(super().name_get())
        for rec in self:
            name = orig_name[rec.id]
            commercial = rec.commercial
            if commercial:
                name = "{} ({})".format(name, commercial)
            result.append((rec.id, name))
        return result
