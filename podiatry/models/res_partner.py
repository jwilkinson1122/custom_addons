from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    #  Patient
    patient_id = fields.One2many(
        comodel_name='podiatry.patient',
        inverse_name='partner_id',
        string="Patients",
    )

    patient_count = fields.Integer(
        string="Patient Count", store=False,
        compute='_compute_patient_count',
    )

    @api.depends('patient_id')
    def _compute_patient_count(self):
        for partner in self:
            partner.patient_count = partner.patient_id
        return

    is_patient = fields.Boolean(
        string="Patient", store=False,
        search='_search_is_patient',
    )

    def _search_is_patient(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('patient_id', search_operator, False)]

    # Practitioner
    # practitioner_id = fields.One2many(
    #     comodel_name='podiatry.practitioner',
    #     inverse_name='partner_id',
    #     string="Practitioners",
    # )

    practitioner_id = fields.Many2one(
        "res.partner",
        string="Main Practitioner",
        domain=[("is_company", "=", False),
                ("practitioner_type", "=", "standalone")],
    )

    other_practitioner_ids = fields.One2many(
        "res.partner",
        "practitioner_id",
        string="Others Positions",
    )

    practitioner_count = fields.Integer(
        string="Practitioner Count", store=False,
        compute='_compute_practitioner_count',
    )

    @api.depends('practitioner_id')
    def _compute_practitioner_count(self):
        for partner in self:
            partner.practitioner_count = partner.practitioner_id
        return

    is_practitioner = fields.Boolean(
        string="Practitioner", store=False,
        search='_search_is_practitioner',
    )

    def _search_is_practitioner(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('practitioner_id', search_operator, False)]

    practitioner_type = fields.Selection(
        [
            ("standalone", "Standalone Practitioner"),
            ("attached", "Attached to existing Practitioner"),
        ],
        compute="_compute_practitioner_type",
        store=True,
        index=True,
        default="standalone",
    )

    # practitioner_id = fields.Many2one(
    #  "res.partner",
    #   string="Main Practitioner",
    #   domain=[("is_company", "=", False),
    #           ("practitioner_type", "=", "standalone")],
    #  )

    # other_practitioner_ids = fields.One2many(
    #   "res.partner",
    #   "practitioner_id",
    #     string="Others Positions",
    #   )

    @api.depends("practitioner_id")
    def _compute_practitioner_type(self):
        for rec in self:
            rec.practitioner_type = "attached" if rec.practitioner_id else "standalone"

    def _basepractitioner_check_context(self, mode):
        """Remove "search_show_all_positions" for non-search mode.
        Keeping it in context can result in unexpected behaviour (ex: reading
        one2many might return wrong result - i.e with "attached practitioner"
        removed even if it"s directly linked to a company).
        Actually, is easier to override a dictionary value to indicate it
        should be ignored...
        """
        if mode != "search" and "search_show_all_positions" in self.env.context:
            result = self.with_context(
                search_show_all_positions={"is_set": False})
        else:
            result = self
        return result

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Display only standalone practitioner matching ``args`` or having
        attached practitioner matching ``args``"""
        ctx = self.env.context
        if (
            ctx.get("search_show_all_positions", {}).get("is_set")
            and not ctx["search_show_all_positions"]["set_value"]
        ):
            args = expression.normalize_domain(args)
            attached_practitioner_args = expression.AND(
                (args, [("practitioner_type", "=", "attached")])
            )
            attached_practitioners = super(
                Partner, self).search(attached_practitioner_args)
            args = expression.OR(
                (
                    expression.AND(
                        ([("practitioner_type", "=", "standalone")], args)),
                    [("other_practitioner_ids", "in", attached_practitioners.ids)],
                )
            )
        return super(Partner, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    @api.model
    def create(self, vals):
        """When creating, use a modified self to alter the context (see
        comment in _basepractitioner_check_context).  Also, we need to ensure
        that the name on an attached practitioner is the same as the name on the
        practitioner it is attached to."""
        modified_self = self._basepractitioner_check_context("create")
        if not vals.get("name") and vals.get("practitioner_id"):
            vals["name"] = modified_self.browse(vals["practitioner_id"]).name
        return super(Partner, modified_self).create(vals)

    def read(self, fields=None, load="_classic_read"):
        modified_self = self._basepractitioner_check_context("read")
        return super(Partner, modified_self).read(fields=fields, load=load)

    def write(self, vals):
        modified_self = self._basepractitioner_check_context("write")
        return super(Partner, modified_self).write(vals)

    def unlink(self):
        modified_self = self._basepractitioner_check_context("unlink")
        return super(Partner, modified_self).unlink()

    def _compute_commercial_partner(self):
        """Returns the partner that is considered the commercial
        entity of this partner. The commercial entity holds the master data
        for all commercial fields (see :py:meth:`~_commercial_fields`)"""
        result = super(Partner, self)._compute_commercial_partner()
        for partner in self:
            if partner.practitioner_type == "attached" and not partner.parent_id:
                partner.commercial_partner_id = partner.practitioner_id
        return result

    def _practitioner_fields(self):
        """Returns the list of practitioner fields that are synced from the parent
        when a partner is attached to him."""
        return ["name", "title"]

    def _practitioner_sync_from_parent(self):
        """Handle sync of practitioner fields when a new parent practitioner entity
        is set, as if they were related fields
        """
        self.ensure_one()
        if self.practitioner_id:
            practitioner_fields = self._practitioner_fields()
            sync_vals = self.practitioner_id._update_fields_values(
                practitioner_fields)
            self.write(sync_vals)

    def update_practitioner(self, vals):
        if self.env.context.get("__update_practitioner_lock"):
            return
        practitioner_fields = self._practitioner_fields()
        practitioner_vals = {field: vals[field]
                             for field in practitioner_fields if field in vals}
        if practitioner_vals:
            self.with_context(__update_practitioner_lock=True).write(
                practitioner_vals)

    def _fields_sync(self, update_values):
        """Sync commercial fields and address fields from company and to
        children, practitioner fields from practitioner and to attached practitioner
        after create/update, just as if those were all modeled as
        fields.related to the parent
        """
        self.ensure_one()
        super(Partner, self)._fields_sync(update_values)
        practitioner_fields = self._practitioner_fields()
        # 1. From UPSTREAM: sync from parent practitioner
        if update_values.get("practitioner_id"):
            self._practitioner_sync_from_parent()
        # 2. To DOWNSTREAM: sync practitioner fields to parent or related
        elif any(field in practitioner_fields for field in update_values):
            update_ids = self.other_practitioner_ids.filtered(
                lambda p: not p.is_company)
            if self.practitioner_id:
                update_ids |= self.practitioner_id
            update_ids.update_practitioner(update_values)

    @api.onchange("practitioner_id")
    def _onchange_practitioner_id(self):
        if self.practitioner_id:
            self.name = self.practitioner_id.name

    @api.onchange("practitioner_type")
    def _onchange_practitioner_type(self):
        if self.practitioner_type == "standalone":
            self.practitioner_id = False
