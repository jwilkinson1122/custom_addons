# -*- coding: utf-8 -*-
from odoo import api, models, _
import logging

_logger = logging.getLogger(__name__)

PARAM_SYNC = "cpq.sync_from_product"
PARAM_SYNC_PRICES = "cpq.sync_prices_from_cpq"   # bool config flag (optional)

class CpqSyncService(models.Model):
    _name = "cpq.sync.service"
    _description = "CPQ Sync Service"

    # ------------------------------
    # helpers
    # ------------------------------
    def _safe_sudo(self, rec):
        try:
            return rec.sudo()
        except Exception:
            return rec

    def _notify_cron(self, title, message, *, success=True, partner_ids=None, group_xmlid="base.group_system"):
        Bus = self._safe_sudo(self.env["bus.bus"])
        payload = {
            "title": title,
            "message": message,
            "type": "success" if success else "danger",
            "sticky": False,
        }
        partners = False
        if partner_ids:
            partners = self._safe_sudo(self.env["res.partner"]).browse(partner_ids).exists()
        else:
            try:
                admins = self._safe_sudo(self.env.ref(group_xmlid))
                partners = admins.users.mapped("partner_id")
            except Exception:
                partners = self.env.user.partner_id
        if partners:
            for p in partners:
                try:
                    Bus._sendone(p, "simple_notification", payload)
                except Exception:
                    _logger.exception("Failed sending bus notification to partner %s", p.id)

    # ------------------------------
    # link backfills
    # ------------------------------
    @api.model
    def backfill_cpq_value_links(self, limit=5000):
        """Ensure bi-directional links between Product values and CPQ values.
        Also copy linked_option_id CPQ → Product when missing.
        """
        PAV  = self._safe_sudo(self.env["product.attribute.value"])
        CPQV = self._safe_sudo(self.env["cpq.attribute.value"])

        # Product → CPQ
        vals_missing = PAV.search([("linked_cpq_value_id", "=", False)], limit=limit)
        for pav in vals_missing:
            cpq_attr = getattr(pav.attribute_id, "linked_cpq_attribute_id", False)
            if not cpq_attr:
                continue
            cpqv = CPQV.search([("attribute_id", "=", cpq_attr.id), ("name", "=", pav.name)], limit=1)
            if cpqv:
                pav.with_context(cpq_sync_silent=True).write({"linked_cpq_value_id": cpqv.id})
                if "linked_product_attribute_value_id" in cpqv._fields:
                    cpqv.with_context(cpq_sync_silent=True).write({"linked_product_attribute_value_id": pav.id})

                # Copy linked_option_id from CPQ → Product (one-time fill)
                if "linked_option_id" in CPQV._fields and "linked_option_id" in PAV._fields:
                    if cpqv.linked_option_id and not pav.linked_option_id:
                        pav.with_context(cpq_sync_silent=True).write(
                            {"linked_option_id": cpqv.linked_option_id.id}
                        )

        # CPQ → Product
        if "linked_product_attribute_value_id" in CPQV._fields:
            reverse_missing = CPQV.search([("linked_product_attribute_value_id", "=", False)], limit=limit)
            for cpqv in reverse_missing:
                pa = getattr(cpqv.attribute_id, "linked_product_attribute_id", False)
                if not pa:
                    continue
                pav = PAV.search([("attribute_id", "=", pa.id), ("name", "=", cpqv.name)], limit=1)
                if pav:
                    cpqv.with_context(cpq_sync_silent=True).write({"linked_product_attribute_value_id": pav.id})
                    if not pav.linked_cpq_value_id:
                        pav.with_context(cpq_sync_silent=True).write({"linked_cpq_value_id": cpqv.id})

        return True

    # ------------------------------
    # price backfill (CPQ → PTAV)
    # ------------------------------
    def _resolve_cpq_value_from_ptav(self, CPQV, ptav):
        """Best-effort CPQ value lookup for a PTAV."""
        # 1) direct virtual cpq id on PTAV
        vid = (getattr(ptav, "x_virtual_cpq_id", "") or "").strip()
        if vid.isdigit():
            cpqv = self._safe_sudo(CPQV).browse(int(vid))
            if cpqv.exists():
                return cpqv

        # 2) via the PAV link
        pav = getattr(ptav, "product_attribute_value_id", False)
        if pav:
            # 2a) reverse link on PAV
            if "linked_cpq_value_id" in pav._fields and pav.linked_cpq_value_id:
                return self._safe_sudo(pav.linked_cpq_value_id)
            # 2b) fallback by (attribute mapped) + name
            pa = pav.attribute_id
            dom = [
                ("attribute_id.linked_product_attribute_id", "=", pa.id),
                ("name", "=", pav.name),
            ]
            cpqv = self._safe_sudo(CPQV).search(dom, limit=1)
            if cpqv:
                return cpqv

        return self.env["cpq.attribute.value"].browse()  # empty

    @api.model
    def backfill_ptav_prices_from_cpq(self, *, ptav_limit=50000, template_ids=None,
                                      push_to_cpq_if_missing=False):
        """Copy price_extra from cpq.attribute.value → product.template.attribute.value.

        Args:
            ptav_limit: cap to avoid massive single transactions.
            template_ids: optional list of product.template IDs to narrow scope.
            push_to_cpq_if_missing: if True, when CPQ.price_extra is empty but PTAV has a value,
                                    push PTAV.price_extra back to CPQ.

        Returns: dict with counters.
        """
        PTAV = self._safe_sudo(self.env["product.template.attribute.value"])
        CPQV = self._safe_sudo(self.env["cpq.attribute.value"])

        domain = []
        if template_ids:
            domain.append(("product_tmpl_id", "in", template_ids))
        ptavs = PTAV.search(domain, limit=ptav_limit)

        updated = 0
        not_found = 0
        pushed = 0

        # epsilon for float compares
        EPS = 1e-9

        for p in ptavs:
            cpqv = self._resolve_cpq_value_from_ptav(CPQV, p)
            if not (cpqv and cpqv.exists()):
                not_found += 1
                continue

            cpq_price = float(getattr(cpqv, "price_extra", 0.0) or 0.0)
            ptav_price = float(getattr(p, "price_extra", 0.0) or 0.0)

            if abs(ptav_price - cpq_price) > EPS:
                if cpq_price:
                    # CPQ → PTAV
                    p.with_context(cpq_sync_silent=True).write({"price_extra": cpq_price})
                    updated += 1
                elif push_to_cpq_if_missing:
                    # PTAV → CPQ (only when CPQ is empty AND you opted in)
                    try:
                        cpqv.with_context(cpq_sync_silent=True).write({"price_extra": ptav_price})
                        pushed += 1
                    except Exception:
                        _logger.exception("Failed pushing price to CPQ value %s", cpqv.id)

        result = {
            "ptavs_seen": len(ptavs),
            "updated_from_cpq": updated,
            "cpq_not_found": not_found,
            "pushed_to_cpq": pushed,
        }
        _logger.info("CPQ price backfill result: %s", result)
        return result

    # ------------------------------
    # one-shot autosync (links + optional prices)
    # ------------------------------
    @api.model
    def run_autosync(self, refresh_existing=True, push_images=True, limit=2000,
                     sync_prices=True, ptav_limit=50000, push_to_cpq_if_missing=False):
        """Link missing Product → CPQ data, refresh names/images, and (optionally) sync prices."""
        Param = self._safe_sudo(self.env["ir.config_parameter"])
        try:
            sync_flag = Param.get_param(PARAM_SYNC)
        except Exception:
            sync_flag = None

        if sync_flag not in ("1", "True", "true", True):
            msg = _("Autosync skipped: setting '%s' is disabled.") % PARAM_SYNC
            _logger.info(msg)
            self._notify_cron(_("CPQ Autosync"), msg, success=True)
            return {"skipped": True, "reason": "Sync disabled"}

        # 1) Link missing
        ProductAttr    = self._safe_sudo(self.env["product.attribute"])
        ProductAttrVal = self._safe_sudo(self.env["product.attribute.value"])

        attrs_missing = ProductAttr.search([("linked_cpq_attribute_id", "=", False)], limit=limit)
        if attrs_missing:
            attrs_missing._ensure_linked_cpq()

        vals_missing = ProductAttrVal.search([("linked_cpq_value_id", "=", False)], limit=limit)
        if vals_missing:
            vals_missing._ensure_linked_cpq_value()

        # 2) Refresh already-linked (optional)
        attrs_refreshed = 0
        vals_refreshed  = 0
        if refresh_existing:
            linked_attrs = ProductAttr.search([("linked_cpq_attribute_id", "!=", False)], limit=limit)
            for pa in linked_attrs:
                try:
                    cpqa = self._safe_sudo(pa.linked_cpq_attribute_id)
                    if cpqa and cpqa.exists() and cpqa.name != pa.name:
                        cpqa.write({"name": pa.name})
                        attrs_refreshed += 1
                except Exception:
                    _logger.exception("Refresh CPQ attribute failed (product.attribute %s)", pa.id)

            linked_vals = ProductAttrVal.search([("linked_cpq_value_id", "!=", False)], limit=limit)
            for pav in linked_vals:
                try:
                    cpqv = self._safe_sudo(pav.linked_cpq_value_id)
                    if not cpqv or not cpqv.exists():
                        continue
                    updates = {}
                    if cpqv.name != pav.name:
                        updates["name"] = pav.name
                    if push_images and "image_128" in cpqv._fields:
                        src = getattr(pav, "image_1920", False) or getattr(pav, "image_128", False)
                        if src and not getattr(cpqv, "image_128", False):
                            updates["image_128"] = src
                    if updates:
                        cpqv.with_context(cpq_sync_silent=True).write(updates)
                        vals_refreshed += 1
                except Exception:
                    _logger.exception("Refresh CPQ value failed (product.attribute.value %s)", pav.id)

        # 3) Prices (optional + can be gated by a setting)
        do_prices = bool(sync_prices)
        try:
            flag_prices = Param.get_param(PARAM_SYNC_PRICES)
            if flag_prices in ("0", "False", "false"):
                do_prices = False
        except Exception:
            pass

        price_result = {}
        if do_prices:
            price_result = self.backfill_ptav_prices_from_cpq(
                ptav_limit=ptav_limit,
                template_ids=None,
                push_to_cpq_if_missing=push_to_cpq_if_missing,
            )

        # notify
        msg = _(
            "Linked %(a_l)d attributes, %(v_l)d values. "
            "Refreshed %(a_r)d attributes, %(v_r)d values."
        ) % dict(
            a_l=len(attrs_missing), v_l=len(vals_missing),
            a_r=attrs_refreshed,   v_r=vals_refreshed,
        )
        if price_result:
            msg += " " + _("Prices updated: %(u)d; not found: %(nf)d; pushed: %(p)d.") % dict(
                u=price_result.get("updated_from_cpq", 0),
                nf=price_result.get("cpq_not_found", 0),
                p=price_result.get("pushed_to_cpq", 0),
            )

        _logger.info("CPQ Autosync: %s", msg)
        self._notify_cron(_("CPQ Autosync Complete"), msg, success=True)

        return {
            "attrs_linked": len(attrs_missing),
            "vals_linked": len(vals_missing),
            "attrs_refreshed": attrs_refreshed,
            "vals_refreshed": vals_refreshed,
            "price_result": price_result,
            "skipped": False,
        }
