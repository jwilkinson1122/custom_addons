import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


SEQ_CODE = "product.product.default_code.cpq"
PARAM_PREFIX = "cpq.default_code_prefix"
PARAM_SYNC   = "cpq.sync_from_product"

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    
    # Persisted as an ir.config_parameter (no need to override set/get values)
    cpq_sync_from_product = fields.Boolean(
        string="Sync from Product",
        config_parameter=PARAM_SYNC,
        help="If enabled, changes to Product attributes/values will be mirrored to CPQ."
    )

    cpq_code_prefix = fields.Char(
        string="Custom Default Code Prefix",
        default="CP-",
        config_parameter=PARAM_PREFIX,
        help="Prefix to use for Custom product internal references (e.g., CP-, ORTHO-, CUSTOM-)."
    )

    cpq_code_preview = fields.Char(
        string="CP Reference Preview",
        compute="_compute_cpq_code_preview",
        help="Preview of the next generated default code (not saved).",
    )
    
    @api.depends("cpq_code_prefix")
    def _compute_cpq_code_preview(self):
        """Show a preview WITHOUT consuming the sequence."""
        IrSequence = self.env["ir.sequence"].sudo()
        seq = IrSequence.search([("code", "=", SEQ_CODE)], limit=1)
        for rec in self:
            prefix = rec.cpq_code_prefix or "CP-"
            if seq:
                num = seq.number_next_actual or 1
                pad = seq.padding or 5
                candidate = f"{num:0{pad}d}"
                rec.cpq_code_preview = f"{prefix}{candidate}"
            else:
                rec.cpq_code_preview = f"{prefix}00001"

    # def action_cpq_backfill_links(self):
    #     self.ensure_one()
    #     self.env["cpq.sync.service"].with_user(self.env.user).backfill_cpq_value_links()
    #     return {
    #         "type": "ir.actions.client", "tag": "display_notification",
    #         "params": {"title": _("CPQ Backfill Complete"),
    #                 "message": _("Links refreshed."),
    #                 "type": "success", "sticky": False}
    #     }

    # def action_cpq_run_autosync(self):
    #     self.ensure_one()
    #     try:
    #         res = self.env["cpq.sync.service"].with_user(self.env.user.id).run_autosync(
    #             refresh_existing=True, push_images=True, limit=2000
    #         )
    #         msg = _(
    #             "Linked %(a_l)d attributes, %(v_l)d values. "
    #             "Refreshed %(a_r)d attributes, %(v_r)d values."
    #         ) % dict(
    #             a_l=res.get("attrs_linked", 0), v_l=res.get("vals_linked", 0),
    #             a_r=res.get("attrs_refreshed", 0), v_r=res.get("vals_refreshed", 0),
    #         )
    #         return {
    #             "type": "ir.actions.client",
    #             "tag": "display_notification",
    #             "params": {"title": _("CPQ Autosync Complete"), "message": msg, "type": "success", "sticky": False},
    #         }
    #     except Exception as e:
    #         return {
    #             "type": "ir.actions.client",
    #             "tag": "display_notification",
    #             "params": {"title": _("CPQ Autosync Failed"), "message": str(e), "type": "danger", "sticky": True},
    #         }