import logging
import json
import base64
import copy
from logging import config
from markupsafe import Markup
from collections import defaultdict
from copy import deepcopy
import urllib.parse
from odoo.tools.translate import _
from odoo import _, api, fields, models, tools, SUPERUSER_ID
from odoo.http import request
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError, ValidationError
from odoo.models import BaseModel, NewId
from odoo.fields import Date, Datetime
from odoo.api import Environment
from odoo.models import BaseModel

_logger = logging.getLogger(__name__)

def ensure_env(env, *fallback_objs):
    """Return a real api.Environment from whatever the caller passed."""
    if isinstance(env, api.Environment):
        return env
    if hasattr(env, "env"):                      # recordset / model
        return env.env
    for obj in fallback_objs:
        e = getattr(obj, "env", None)
        if e:
            return e
    raise ValueError("No valid Odoo Environment available")

def env_with_context(env, **ctx):
    """Return a NEW Environment with extra context."""
    env = ensure_env(env)
    new_ctx = dict(env.context or {})
    new_ctx.update(ctx or {})
    return api.Environment(env.cr, env.uid, new_ctx)

def env_as_sudo(env, uid=None):
    """Return a NEW Environment with sudo (or specific uid)."""
    env = ensure_env(env)
    return api.Environment(env.cr, uid or SUPERUSER_ID, env.context)

def get_cpq_config_dict(raw):
    """
    Parse any incoming CPQ config to a canonical dict with:
      - selected: {left: {}, right: {}, shared: {}}
      - splitByAttrMap: {<attr_id>: True/False}
      - split: bool

    IMPORTANT CHANGE:
    We no longer collapse equal left/right selections into `shared`
    when we're in Bilateral Split. That collapse was causing the
    Right cell to disappear in the summary.
    """
    # --- 1) Parse input into a dict
    if isinstance(raw, dict):
        config = raw.copy()
    elif isinstance(raw, str):
        try:
            config = json.loads(raw)
            if not isinstance(config, dict):
                return {}
        except Exception:
            return {}
    else:
        return {}

    # --- 2) Ensure selected has left/right/shared buckets
    sel = config.get("selected", {})
    if isinstance(sel, dict) and not any(k in sel for k in ("left", "right", "shared")):
        # flat → shared
        shared = {}
        for k, v in sel.items():
            try:
                int_k = int(k)
            except (ValueError, TypeError):
                continue
            if isinstance(v, dict):
                shared[str(int_k)] = v
            elif v is True or isinstance(v, int):
                shared[str(int_k)] = {"id": int_k, "value": int_k}
        config["selected"] = {"left": {}, "right": {}, "shared": shared}

    config.setdefault("selected", {"left": {}, "right": {}, "shared": {}})

    grouped = config.get("grouped") or config.get("groupedCombinationForBackend", {})
    prefs   = config.get("cpqPreferences", []) or []
    ptal    = config.get("ptal_ids", []) or []

    # --- 3) Derive splitByAttrMap from preferences (first pass)
    split_map = {}
    if isinstance(grouped, dict) and prefs:
        for p in prefs:
            vid = p.get("value_id")
            aid = p.get("attribute_id")
            if vid and grouped.get(str(vid)):
                split_map[str(aid)] = True
        if split_map:
            config["splitByAttrMap"] = split_map

    # --- 4) Fallback split map from grouped + ptal_ids (second pass)
    if not config.get("splitByAttrMap"):
        for attr in ptal:
            aid = attr.get("id")
            for val in attr.get("values", []) or []:
                if grouped.get(str(val.get("id"))):
                    split_map[str(aid)] = True
        if split_map:
            config["splitByAttrMap"] = split_map

    # --- 5) Normalize splitByAttrMap keys to strings
    if "splitByAttrMap" in config:
        config["splitByAttrMap"] = {str(k): bool(v) for k, v in (config["splitByAttrMap"] or {}).items()}
    sbam = config.get("splitByAttrMap", {})

    # --- 6) DO NOT collapse equal LT/RT into shared for Bilateral Split
    # Old behavior (removed/guarded) was moving equal sides to `shared` and
    # removing the attr from splitByAttrMap, which made RT vanish in the summary.
    laterality = (config.get("laterality") or "bilateral").lower()
    incoming_split = bool(sbam)

    # Only collapse when we're NOT in Bilateral Split.
    # (Keep legacy behavior for non-split contexts if you still want it.)
    if not (laterality == "bilateral" and incoming_split):
        for aid in list(sbam.keys()):
            key = str(aid)
            left  = config["selected"]["left"].get(key)
            right = config["selected"]["right"].get(key)
            if isinstance(left, dict) and isinstance(right, dict) and left.get("value") == right.get("value"):
                config["selected"]["shared"][key] = left
                config["selected"]["left"].pop(key, None)
                config["selected"]["right"].pop(key, None)
                sbam.pop(aid, None)
                _logger.debug("[ConfigDict] Collapsed attr %s into shared (non-split mode)", aid)

    # --- 7) Finalize split flag
    config["split"] = bool(config.get("splitByAttrMap"))
    _logger.debug("[ConfigDict] config['split'] → %s; laterality=%s", config["split"], laterality)

    return config

def resolve_cpq_preferences_for_product(odoo_env, partner_id, product_tmpl_id):
    Rule = odoo_env['cpq.rules.product'].sudo()
    rules = Rule.search([
        ('partner_id', 'child_of', partner_id),
        ('product_tmpl_id', 'in', [False, product_tmpl_id]),
        ('active', '=', True),
    ])

    selected = {}
    detailed = []

    for rule in rules:
        cpq_val = rule.value_id
        if not rule.attribute_id or not cpq_val:
            continue

        final_id = cpq_val.id

        # --- Hybrid preferred flags ---
        is_preferred = True
        is_preferred_left = getattr(rule, 'is_preferred_left', None)
        is_preferred_right = getattr(rule, 'is_preferred_right', None)

        # If left/right not defined on the rule, fallback to True for both for compatibility
        # (you can adjust this logic if your rules support per-side preferred)
        if is_preferred_left is None:
            is_preferred_left = is_preferred
        if is_preferred_right is None:
            is_preferred_right = is_preferred

        selected[str(final_id)] = {
            "id": final_id,
            "isPreferred": is_preferred,
            "isPreferredLeft": is_preferred_left,
            "isPreferredRight": is_preferred_right,
            "note": rule.note or "",
        }

        detailed.append({
            "attribute_id": rule.attribute_id.id,
            "attribute_name": rule.attribute_id.display_name,
            "value_id": final_id,
            "value_name": cpq_val.display_name,
            "scope": rule.scope,
            "note": rule.note or "",
            "isPreferred": is_preferred,
            "isPreferredLeft": is_preferred_left,
            "isPreferredRight": is_preferred_right,
        })

    return {
        "selected": selected,
        "detailed": detailed,
    }

def format_currency(amount, odoo_env):
    return formatLang(odoo_env, amount, currency_obj=odoo_env.user.company_id.currency_id)

def enrich_selected_with_preferences(selected, preferences):
    selected = copy.deepcopy(selected or {})
    for ptal in preferences or []:
        for ptav in ptal.get("ptav_ids", []):
            ptav_id = str(ptav["id"])
            note = ptav.get("note")
            # New: grab side-specific flags, fallback to isPreferred for both
            is_preferred = ptav.get("isPreferred", False)
            is_preferred_left = ptav.get("isPreferredLeft", is_preferred)
            is_preferred_right = ptav.get("isPreferredRight", is_preferred)
            target = selected

            if "left" in selected and "right" in selected:
                for side in ("left", "right", "shared"):
                    if side in target:
                        entry = target[side].setdefault(ptav_id, {})
                        # Side-specific preferred
                        if "isPreferredLeft" not in entry and side == "left":
                            entry["isPreferredLeft"] = is_preferred_left
                        if "isPreferredRight" not in entry and side == "right":
                            entry["isPreferredRight"] = is_preferred_right
                        # For shared, you might want to set both
                        if "isPreferredLeft" not in entry and side == "shared":
                            entry["isPreferredLeft"] = is_preferred_left
                        if "isPreferredRight" not in entry and side == "shared":
                            entry["isPreferredRight"] = is_preferred_right
                        # Fallback global flag for legacy code
                        if "isPreferred" not in entry and is_preferred:
                            entry["isPreferred"] = is_preferred
                        if "note" not in entry and note:
                            entry["note"] = note
            else:
                entry = target.setdefault(ptav_id, {})
                # Set both per-side for single-bucket legacy shape
                if "isPreferredLeft" not in entry:
                    entry["isPreferredLeft"] = is_preferred_left
                if "isPreferredRight" not in entry:
                    entry["isPreferredRight"] = is_preferred_right
                if "isPreferred" not in entry and is_preferred:
                    entry["isPreferred"] = is_preferred
                if "note" not in entry and note:
                    entry["note"] = note
    return selected

def find_ptav_value_by_attr_id(selected_dict, attr_id, attr_id_map=None):
    attr_id_str = str(attr_id)
    for ptav_id, meta in selected_dict.items():
        ptav_id_str = str(ptav_id)
        if not isinstance(meta, dict):
            continue

        linked_id = str(meta.get("linked_option_id", {}).get("id")) if "linked_option_id" in meta else None
        attr_from_meta = str(meta.get("attr_id")) if "attr_id" in meta else None

        if linked_id == attr_id_str or attr_from_meta == attr_id_str:
            return ptav_id_str

        if attr_id_map and str(attr_id_map.get(ptav_id_str)) == attr_id_str:
            return ptav_id_str
    return None

def normalize_selected_keys(selected):
    return {
        "left": {str(k): v for k, v in (selected.get("left", {}) or {}).items()},
        "right": {str(k): v for k, v in (selected.get("right", {}) or {}).items()},
        "shared": {str(k): v for k, v in (selected.get("shared", {}) or {}).items()},
    }

def normalize_selected_values(selected):
    """
    Ensures all selected values are dicts with at least an 'id' and 'value'.
    Converts raw ints/bools into dict form.
    """
    normalized = {}
    for side in ("left", "right", "shared"):
        side_vals = selected.get(side, {})
        norm = {}
        for pid, val in side_vals.items():
            if not str(pid).isdigit():
                # _logger.warning("[Normalize] Removing non-digit key from '%s': %s", side, pid)
                continue  # 🚫 Skip "value": "left" type junk keys
            if isinstance(val, dict):
                norm[pid] = val
            else:
                norm[pid] = {"id": val, "value": val}
        normalized[side] = norm
    return normalized

def normalize_selected(selected):
    # Canonicalizes selected keys: flat, left/right/shared etc
    # This should mirror your JS utils' `normalizeSelectedStructure`
    if not selected:
        return {}
    if isinstance(selected, dict) and any(k in selected for k in ("left", "right", "shared")):
        return selected
    # Fallback: treat as flat and wrap as shared for bilateral, left for left, etc.
    return {"shared": selected}

USE_LINKED_LOOKUP = True

def coerce_match_pid(side_dict, attr_id, attr_id_map):
    for pid in side_dict:
        try:
            coerced_pid = str(int(pid))  # safe cast to match keys in attr_id_map
            mapped_attr = attr_id_map.get(coerced_pid)
            if str(mapped_attr) == str(attr_id):
                return coerced_pid
        except Exception:
            continue
    return None   

def ensure_flattened_selected(config):
    """
    If config['selected'] is in left/right/shared shape,
    flatten shared (and optionally left/right) back to top-level keys.
    """
    selected = config.get("selected", {})
    if isinstance(selected, dict):
        # This means it's the nested/structured style
        if "shared" in selected:
            # Only flatten if shared contains keys
            flat = {}
            # flatten shared
            for k, v in (selected.get("shared") or {}).items():
                flat[k] = v
            # optionally: also flatten left/right, depending on your logic
            for side in ("left", "right"):
                for k, v in (selected.get(side) or {}).items():
                    flat[k] = v
            config["selected"] = flat
    return config

def build_summary(config):
    """
    Build summary rows for rendering (LT/RT/Shared/Split/Match/Price),
    with correct behavior for Left-only and Right-only laterality.
    """

    def flatten_attributes(attrs):
        flat = []
        for attr in attrs or []:
            if attr.get("is_group") and attr.get("children"):
                flat.extend(flatten_attributes(attr["children"]))
            else:
                flat.append(attr)
        return flat

    sel = config.get("selected") or {}
    selected = {
        "left":   (sel.get("left")   or {}) if isinstance(sel, dict) else {},
        "right":  (sel.get("right")  or {}) if isinstance(sel, dict) else {},
        "shared": (sel.get("shared") or {}) if isinstance(sel, dict) else {},
    }
    ptal_ids = config.get("ptal_ids") or []
    split_map = config.get("splitByAttrMap") or {}
    split_global = bool(config.get("split", False))
    laterality = config.get("laterality", "bilateral")
    qty = int(config.get("quantity_to_make", 1) or 1)

    all_attrs = flatten_attributes(ptal_ids)
    rows = []

    def get_selected_val(values, bucket):
        """Return the PTAL value dict matched by virtual id or id, merged with bucket meta."""
        if not bucket:
            return None
        for v in values or []:
            x_id = str(v.get("x_virtual_cpq_id") or "")
            v_id = str(v.get("id"))
            for key in (x_id, v_id):
                if key and key in bucket:
                    meta = bucket[key]
                    merged = dict(v)
                    if isinstance(meta, dict):
                        merged.update(meta)
                    else:
                        merged.setdefault("value", meta)
                    return merged
        return None

    if laterality in ("left", "right"):
        want_side = laterality  
        for attr in all_attrs:
            attr_id = str(attr["id"])
            attr_name = attr.get("name", f"Attribute {attr_id}")
            values = attr.get("values") or attr.get("ptav_ids") or []

            val = get_selected_val(values, selected[want_side]) or get_selected_val(values, selected["shared"])
            if not val:
                continue

            val_name = val.get("name", "-")
            price_extra = float(val.get("price_extra") or 0.0) * qty
            left_txt = val_name if want_side == "left" else "-"
            right_txt = val_name if want_side == "right" else "-"

            rows.append({
                "key": f"summary-{attr_id}",
                "label": attr_name,
                "left": left_txt,
                "right": right_txt,
                "shared": "-",         
                "isSplit": False,    
                "match": False,         
                "priceExtra": price_extra,
                "note": val.get("note", "") or "",
                "isPreferred": bool(val.get("isPreferred") or val.get("isPreferredLeft") or val.get("isPreferredRight")),
            })
        return rows

    for attr in all_attrs:
        attr_id = str(attr["id"])
        attr_name = attr.get("name", f"Attribute {attr_id}")
        values = attr.get("values") or attr.get("ptav_ids") or []
        is_split = bool(split_map.get(attr_id) or split_global)

        if is_split:
            left_val = get_selected_val(values, selected["left"]) or get_selected_val(values, selected["shared"])
            right_val = get_selected_val(values, selected["right"]) or get_selected_val(values, selected["shared"])
            if not left_val and not right_val:
                continue

            left_name = left_val.get("name") if left_val else "-"
            right_name = right_val.get("name") if right_val else "-"
            price_extra = ((float(left_val.get("price_extra") or 0.0) if left_val else 0.0) +
                           (float(right_val.get("price_extra") or 0.0) if right_val else 0.0)) * qty

            rows.append({
                "key": f"summary-{attr_id}",
                "label": attr_name,
                "left": left_name,
                "right": right_name,
                "shared": "-",
                "isSplit": True,
                "match": bool(left_val and right_val and str(left_val.get("id")) == str(right_val.get("id"))),
                "priceExtra": price_extra,
                "note": None,
                "noteLeft": (left_val or {}).get("note", "") if left_val else "",
                "noteRight": (right_val or {}).get("note", "") if right_val else "",
                "isPreferred": None,
                "isPreferredLeft": bool((left_val or {}).get("isPreferredLeft") or (left_val or {}).get("isPreferred")),
                "isPreferredRight": bool((right_val or {}).get("isPreferredRight") or (right_val or {}).get("isPreferred")),
            })
        else:
            val = get_selected_val(values, selected["shared"]) or \
                  get_selected_val(values, selected["left"]) or \
                  get_selected_val(values, selected["right"])
            if not val:
                continue

            val_name = val.get("name", "-")
            price_extra = float(val.get("price_extra") or 0.0) * 2 * qty

            rows.append({
                "key": f"summary-{attr_id}",
                "label": attr_name,
                "left": val_name,
                "right": val_name,
                "shared": val_name,
                "isSplit": False,
                "match": True,          
                "priceExtra": price_extra,
                "note": val.get("note", "") or "",
                "noteLeft": None,
                "noteRight": None,
                "isPreferred": bool(val.get("isPreferred") or val.get("isPreferredLeft") or val.get("isPreferredRight")),
            })

    return rows

def rebuild_selected_dict(config):
    raw = config.get("selected", {})
    rebuilt = {}

    for k, v in raw.items():
        if k in ("left", "right", "shared") and isinstance(v, dict):
            rebuilt[k] = {
                int(inner_k): inner_v
                for inner_k, inner_v in v.items()
                if str(inner_k).isdigit()
            }
        elif str(k).isdigit():
            rebuilt[int(k)] = v
        else:
            _logger.warning("[Custom] Skipping non-integer PTAV ID key: %s", k)
    return rebuilt

def split_selected_dict_by_attribute(selected, ptal_ids, split_by_attr_map, laterality):
    """
    Given a flat selected={ptav_id: meta} dict, bucket each ptav into one of:
      - left
      - right
      - shared
    based on split_by_attr_map and laterality.
    """
    def _build_attr_map(ptal_ids):
        m = {}
        for attr in ptal_ids:
            aid = attr["id"]
            for v in attr.get("ptav_ids") or attr.get("values") or []:
                vid = str(v.get("x_virtual_cpq_id") or v.get("id"))
                m[vid] = aid
        return m

    attr_id_map = _build_attr_map(ptal_ids)
    result = {"left": {}, "right": {}, "shared": {}}

    for raw_pid, raw_meta in selected.items():
        pid = str(raw_pid)
        meta = copy.deepcopy(raw_meta) if isinstance(raw_meta, dict) else {}
        aid = attr_id_map.get(pid)
        split_flag = bool(aid and split_by_attr_map.get(aid))

        if laterality == "left":
            result["left"][pid] = meta
        elif laterality == "right":
            result["right"][pid] = meta
        else:  # bilateral
            if split_flag:
                result["left"][pid] = meta
                result["right"][pid] = meta
            else:
                result["shared"][pid] = meta

    return result

def unflatten_selection_dict(flat):
    """Rebuilds a {id: {...}} mapping from flattened keys like '3:id'."""
    nested = {}
    for key, value in flat.items():
        if ':' not in key:
            continue
        id_str, field = key.split(':', 1)
        try:
            id_int = int(id_str)
        except Exception:
            continue
        nested.setdefault(id_int, {})[field] = value
    return nested

def extract_cpq_ptavs(
    odoo_env,
    product_template,
    config_or_selected,
    *,
    create_missing_pavs=True,   # auto-create product.attribute.value when missing
    attach_to_template=True,    # ensure template has attribute line/value -> real PTAV
    reuse_pav_by_name=True,     # try reuse by (attribute, name) before creating
    sudo_create=True,           # do creations as sudo
):
    """
    Return (ptav_records, custom_dict, structured_selected).

    Resilient to:
      - odoo_env being anything (will fall back to product_template.env)
      - selected passed as dict/flattened/grouped/list/set/tuple/single id/booleans
      - missing optional fields (x_virtual_cpq_id, linked_option_id, images, backlinks)
    """
    # -------------------- guard rails --------------------
    # Always trust the template’s env/cursor (callers sometimes pass a dict as env)
    if not getattr(product_template, "exists", None) or not product_template.exists():
        # Still return proper empty recordset from *some* env
        # Try given env first if it *looks* like an Environment, else fallback to template.env
        safe_env = (getattr(odoo_env, "cr", None) and isinstance(odoo_env, api.Environment)) and odoo_env or None
        if not safe_env:
            try:
                safe_env = product_template.env
            except Exception:
                safe_env = None
        if not safe_env:
            # Last resort: fail quietly with empty-ish returns
            return [], {}, {"left": {}, "right": {}, "shared": {}}
        return safe_env["product.template.attribute.value"].browse(), {}, {"left": {}, "right": {}, "shared": {}}

    base_env = getattr(product_template, "env", None) or getattr(odoo_env, "env", None) or odoo_env
    if not getattr(base_env, "cr", None):
        base_env = product_template.env

    company = product_template.company_id
    if company:
        base_env = env_with_context(base_env, allowed_company_ids=[company.id])

    # ⛔️ Old (wrong): create_env = base_env.sudo() if sudo_create else base_env
    # ✅ New:
    create_env = env_as_sudo(base_env) if sudo_create else base_env

    # Models (reads in base_env; creates in create_env)
    PTAV_read  = base_env["product.template.attribute.value"]
    PTAL_read  = base_env["product.template.attribute.line"]
    PAV_read   = base_env["product.attribute.value"]
    PATTR_read = base_env["product.attribute"]
    CPQV_read  = base_env["cpq.attribute.value"]

    PTAL_create = create_env["product.template.attribute.line"]
    PTAV_create = create_env["product.template.attribute.value"]
    PAV_create  = create_env["product.attribute.value"]
    PATTR_create= create_env["product.attribute"]

    # -------------------- helpers --------------------
    def _ensure_product_attribute(cpq_attr):
        """Return a product.attribute linked to cpq_attr, creating/linking if needed."""
        if not cpq_attr or not cpq_attr.exists():
            return False

        linked = getattr(cpq_attr, "linked_product_attribute_id", False)
        if linked and linked.exists():
            return linked

        linked = PATTR_read.search([("name", "=", cpq_attr.name)], limit=1)
        if not linked and create_missing_pavs:
            linked = PATTR_create.create({"name": cpq_attr.name, "create_variant": "no_variant"})

        # Best-effort backlink
        if linked and "linked_product_attribute_id" in cpq_attr._fields:
            try:
                cpq_attr.sudo().write({"linked_product_attribute_id": linked.id})
            except Exception:
                pass
        return linked

    def _ensure_pav_for_cpq_value(linked_attr, cpq_val):
        """Resolve or create a product.attribute.value for a cpq.attribute.value."""
        pav = False

        # 1) try via product.options bridge if present
        try:
            opt = getattr(cpq_val, "linked_option_id", False)
            if opt and getattr(opt, "product_attribute_value_id", False):
                pav = opt.product_attribute_value_id
        except Exception:
            pav = False

        # 2) reuse by (attribute, name)
        if not pav and reuse_pav_by_name:
            pav = PAV_read.search([("attribute_id", "=", linked_attr.id),("name", "=", cpq_val.name)], limit=1)

        # 3) create
        if not pav and create_missing_pavs:
            pav = PAV_create.create({"attribute_id": linked_attr.id, "name": cpq_val.name})

        # backlink on cpq.value if a field exists
        if pav:
            for f in ("linked_product_attribute_value_id", "x_linked_pav_id", "x_linked_pav"):
                if f in cpq_val._fields:
                    try:
                        cpq_val.sudo().write({f: pav.id})
                    except Exception:
                        pass
                    break
            # optional: mirror CPQ image → PAV (one-time)
            try:
                if hasattr(PAV_read, "image_1920") and getattr(cpq_val, "image_128", False) and not pav.image_1920:
                    pav.sudo().write({"image_1920": cpq_val.image_128})
            except Exception:
                pass
            # try:
            #     if "image_1920" in PAV_read._fields and getattr(cpq_val, "image_128", False) and not pav.image_1920:
            #         pav.sudo().write({"image_1920": cpq_val.image_128})
            # except Exception:
            #     pass
            # keep options bridge consistent
            if hasattr(pav, "linked_option_id") and hasattr(cpq_val, "linked_option_id") and cpq_val.linked_option_id:
                try:
                    pav.sudo().write({"linked_option_id": cpq_val.linked_option_id.id})
                except Exception:
                    pass
        return pav
    
    def _ensure_ptav_on_template(pav, linked_attr, *, cpq_val=None):
        """Make sure the template has a PTAV for the given PAV + sync metadata."""
        # Ensure PTAL contains this PAV (unchanged)
        ptal = PTAL_read.search([
            ("product_tmpl_id", "=", product_template.id),
            ("attribute_id", "=", linked_attr.id),
        ], limit=1)
        if not ptal:
            ptal = PTAL_create.create({
                "product_tmpl_id": product_template.id,
                "attribute_id": linked_attr.id,
                "value_ids": [(4, pav.id)],
            })
        elif pav.id not in ptal.value_ids.ids:
            ptal.sudo().write({"value_ids": [(4, pav.id)]})

        # Find/create PTAV (unchanged)
        ptav = PTAV_read.search([
            ("product_tmpl_id", "=", product_template.id),
            ("product_attribute_value_id", "=", pav.id),
        ], limit=1)
        if not ptav:
            ptav = PTAV_read.search([
                ("attribute_line_id", "=", ptal.id),
                ("product_attribute_value_id", "=", pav.id),
            ], limit=1)
        if not ptav:
            ptav = PTAV_create.create({
                "product_tmpl_id": product_template.id,
                "attribute_line_id": ptal.id,
                "product_attribute_value_id": pav.id,
            })

        # ---- NEW: sync metadata from CPQ value ----
        if cpq_val:
            # 1) price_extra belongs on PTAV (per template)
            try:
                cpq_price = float(getattr(cpq_val, "price_extra", 0.0) or 0.0)
            except Exception:
                cpq_price = 0.0
            # only write if different to avoid churn
            if abs((ptav.price_extra or 0.0) - cpq_price) > 1e-9:
                ptav.sudo().write({"price_extra": cpq_price})

            # 2) store virtual backlink for quick reverse-lookup/validate
            if "x_virtual_cpq_id" in ptav._fields:
                try:
                    ptav.sudo().write({"x_virtual_cpq_id": str(cpq_val.id)})
                except Exception:
                    pass

            # 3) optionally mirror images onto the PAV once, if you like
            try:
                if hasattr(PAV_read, "image_1920") and getattr(cpq_val, "image_128", False) and not pav.image_1920:
                    pav.sudo().write({"image_1920": cpq_val.image_128})
            except Exception:
                pass

            # 4) if you keep a bridge to product.options or reverse link, sync it now
            if hasattr(pav, "linked_option_id") and hasattr(cpq_val, "linked_option_id") and cpq_val.linked_option_id:
                try:
                    pav.sudo().write({"linked_option_id": cpq_val.linked_option_id.id})
                except Exception:
                    pass

        return ptav

    
    # def _ensure_ptav_on_template(pav, linked_attr, *, cpq_val=None):
    #     """Make sure the template has a PTAV for the given PAV."""
    #     ptal = PTAL_read.search([
    #         ("product_tmpl_id", "=", product_template.id),
    #         ("attribute_id", "=", linked_attr.id),
    #     ], limit=1)

    #     if not ptal:
    #         ptal = PTAL_create.create({
    #             "product_tmpl_id": product_template.id,
    #             "attribute_id": linked_attr.id,
    #             "value_ids": [(4, pav.id)],
    #         })
    #     elif pav.id not in ptal.value_ids.ids:
    #         ptal.sudo().write({"value_ids": [(4, pav.id)]})

    #     ptav = PTAV_read.search([
    #         ("product_tmpl_id", "=", product_template.id),
    #         ("product_attribute_value_id", "=", pav.id),
    #     ], limit=1)

    #     if not ptav:
    #         ptav = PTAV_read.search([
    #             ("attribute_line_id", "=", ptal.id),
    #             ("product_attribute_value_id", "=", pav.id),
    #         ], limit=1)

    #     if not ptav:
    #         ptav = PTAV_create.create({
    #             "product_tmpl_id": product_template.id,
    #             "attribute_line_id": ptal.id,
    #             "product_attribute_value_id": pav.id,
    #         })

    #     if ptav and cpq_val is not None and "x_virtual_cpq_id" in ptav._fields:
    #         try:
    #             ptav.sudo().write({"x_virtual_cpq_id": str(cpq_val.id)})
    #         except Exception:
    #             pass

    #     return ptav

    # -------------------- normalize incoming selection --------------------
    def _to_selected_buckets(obj):
        """
        Returns a dict with {left, right, shared} buckets.
        Accepts: dicts (flattened or grouped), list/tuple/set of ids, single id, or {id: True} maps.
        """
        if obj is None:
            return {"left": {}, "right": {}, "shared": {}}

        # {selected: ...}
        if isinstance(obj, dict) and "selected" in obj and isinstance(
            obj["selected"], (dict, list, tuple, set, int, str)
        ):
            return _to_selected_buckets(obj["selected"])

        # {grouped: {...}} → collapse to shared
        if isinstance(obj, dict) and "grouped" in obj and isinstance(obj["grouped"], dict):
            flat = {}
            for _k, bucket in (obj["grouped"] or {}).items():
                if isinstance(bucket, dict):
                    flat.update(bucket)
            return {"left": {}, "right": {}, "shared": flat}

        # already has left/right/shared
        if isinstance(obj, dict) and {"left", "right", "shared"} <= set(obj.keys()):
            return {
                "left":   obj.get("left")   or {},
                "right":  obj.get("right")  or {},
                "shared": obj.get("shared") or {},
            }

        # flat dict {id or key: value/True/dict}
        if isinstance(obj, dict):
            return {"left": {}, "right": {}, "shared": dict(obj)}

        # list/tuple/set of ids
        if isinstance(obj, (list, tuple, set)):
            shared = {}
            for x in obj:
                shared[str(x)] = {"value": x}
            return {"left": {}, "right": {}, "shared": shared}

        # single id
        if isinstance(obj, (int, str)):
            return {"left": {}, "right": {}, "shared": {str(obj): {"value": obj}}}

        return {"left": {}, "right": {}, "shared": {}}

    buckets = _to_selected_buckets(config_or_selected)

    # -------------------- unify buckets for processing --------------------
    combined = {}
    for side in ("left", "right", "shared"):
        sd = buckets.get(side) or {}
        if isinstance(sd, dict):
            combined.update(sd)

    # -------------------- utilities --------------------
    def _resolve_raw_id(k, v):
        """Get a raw id from a (key, value) selection entry."""
        if isinstance(v, dict):
            return v.get("id") or v.get("value") or k
        if v is True:
            return k
        return v or k

    def _find_ptav_for_any_id(pid_str):
        """Try treat pid_str as PTAV id; else lookup by virtual cpq id."""
        # direct PTAV id?
        ipid = None
        try:
            ipid = int(pid_str)
        except Exception:
            pass
        if ipid is not None:
            p = PTAV_read.browse(ipid)
            if p.exists() and p.product_tmpl_id.id == product_template.id:
                return p
        # virtual backlink?
        return PTAV_read.search([
            ("product_tmpl_id", "=", product_template.id),
            ("x_virtual_cpq_id", "=", pid_str),
        ], limit=1)

    # -------------------- main build --------------------
    ptav_recs = PTAV_read.browse()  # empty recordset
    custom_dict = {}

    with base_env.cr.savepoint():
        for key, val in (combined or {}).items():
            raw_id = _resolve_raw_id(key, val)
            pid = str(raw_id)

            # A) already a PTAV reference?
            ptav = _find_ptav_for_any_id(pid)
            if ptav:
                ptav_recs |= ptav
                if getattr(ptav, "is_custom", False):
                    custom_dict[ptav] = (val.get("value") if isinstance(val, dict) else val)
                continue

            # B) treat as cpq.attribute.value id
            try:
                cpq_id = int(pid)
            except Exception:
                _logger.warning("[CPQ] Selection id %r is not an int; skipping", pid)
                continue

            cpq_val = CPQV_read.browse(cpq_id)
            if not cpq_val or not cpq_val.exists():
                _logger.warning("[CPQ] No cpq.attribute.value for id=%r — skipping", pid)
                continue

            cpq_attr = cpq_val.attribute_id
            linked_attr = _ensure_product_attribute(cpq_attr)
            if not linked_attr:
                _logger.warning("[CPQ] cpq.value %s has no linked product.attribute — skipping", cpq_val.id)
                continue

            pav = _ensure_pav_for_cpq_value(linked_attr, cpq_val)
            if not pav:
                _logger.warning("[CPQ] Could not resolve/create PAV for cpq.value id=%s — skipping", cpq_val.id)
                continue

            real_ptav = _ensure_ptav_on_template(pav, linked_attr, cpq_val=cpq_val) if attach_to_template else False
            if real_ptav:
                ptav_recs |= real_ptav
                if bool(getattr(cpq_val, "is_custom", False)):
                    custom_dict[real_ptav] = (val.get("value") if isinstance(val, dict) else val)
                continue

            # C) fallback: ephemeral (not persisted)
            virtual = PTAV_read.new({
                "product_tmpl_id": product_template.id,
                "attribute_id": linked_attr.id,
                "product_attribute_value_id": pav.id,
                "price_extra": (getattr(cpq_val, "price_extra", 0.0) or 0.0),
                "name": cpq_val.name,
            })
            if "x_virtual_cpq_id" in virtual._fields:
                try:
                    setattr(virtual, "x_virtual_cpq_id", str(cpq_val.id))
                except Exception:
                    pass
            ptav_recs += virtual
            if bool(getattr(cpq_val, "is_custom", False)):
                custom_dict[virtual] = (val.get("value") if isinstance(val, dict) else val)

    # Helpful trace (safe with NewId)
    try:
        for p in ptav_recs:
            _logger.debug(
                "[CPQ] PTAV -> %s | id=%s | pav_id=%s | virtual=%s | x_virtual_cpq_id=%s",
                p.display_name,
                p.id,
                p.product_attribute_value_id.id if p.product_attribute_value_id else None,
                isinstance(p.id, NewId),
                getattr(p, "x_virtual_cpq_id", "—"),
            )
    except Exception:
        pass

    return ptav_recs, custom_dict, buckets

def flatten_combination_ids(combination):
    ids = []
    for side in ("left", "right", "shared"):
        side_vals = combination.get(side)
        if isinstance(side_vals, dict):
            ids.extend(side_vals.keys())
    if not ids:
        selected = combination.get("selected")
        if isinstance(selected, dict):
            ids.extend(selected.keys())
        else:
            ids.extend(combination.keys())
    return list(ids)

def safe_int_keys(data):
    raw_keys = flatten_combination_ids(data)
    return [int(k) for k in raw_keys if str(k).isdigit()]

def get_validated_and_original_selected(template, config_dict):
    config_dict = ensure_flattened_selected(config_dict)
    original_selected = dict(config_dict.get("selected", {}))
    if not original_selected:
        grouped = config_dict.get("grouped")
        if grouped:
            original_selected = flatten_grouped_selection(grouped)
        else:
            original_selected = rebuild_selected_dict(config_dict)
    ptav_ids, custom_dict, cleaned_selected = extract_cpq_ptavs(template.env, template, original_selected)

    valid_ptav_ids = {
        str(ptav.x_virtual_cpq_id or ptav.id) for ptav in ptav_ids if (ptav.x_virtual_cpq_id or ptav.id)
    }
    sanitized_selected = {k: v if isinstance(v, dict) else {"value": v} for k, v in original_selected.items() if str(k) in valid_ptav_ids}
    config_dict["selected"] = cleaned_selected
    return ptav_ids, custom_dict, original_selected, sanitized_selected

def generate_virtual_ptavs_from_cpq(
    odoo_env,
    product_tmpl,
    cpq_value_ids,
    *,
    sudo_create: bool = True,
):
    """
    Build a *virtual* (ephemeral) PTAV recordset for the given CPQ values,
    aligned to the product template's company context. No DB writes occur,
    aside from best-effort backlinks via sudo when available.

    Returns: recordset of product.template.attribute.value (may contain NewId rows).
    """
    # ---------- guard rails ----------
    # Ensure we have a real template and a usable env
    try:
        if not getattr(product_tmpl, "exists", None) or not product_tmpl.exists():
            # return an empty PTAV recordset from *some* env if possible
            env_try = getattr(odoo_env, "env", None) or getattr(product_tmpl, "env", None) or odoo_env
            if getattr(env_try, "cr", None):
                return env_try["product.template.attribute.value"].browse()
            return []  # last resort
    except Exception:
        env_try = getattr(product_tmpl, "env", None)
        if env_try and getattr(env_try, "cr", None):
            return env_try["product.template.attribute.value"].browse()
        return []

    # ---------- env normalization (no direct .sudo/.with_context) ----------
    env = ensure_env(odoo_env, product_tmpl)
    if getattr(product_tmpl, "company_id", False):
        env = env_with_context(env, allowed_company_ids=[product_tmpl.company_id.id])

    read_env   = env
    create_env = env_as_sudo(read_env) if sudo_create else read_env

    # ---------- models ----------
    PTAV_r  = read_env["product.template.attribute.value"]
    PATTR_r = read_env["product.attribute"]
    PAV_r   = read_env["product.attribute.value"]

    PATTR_c = create_env["product.attribute"]
    # PAV_c not needed since we *don’t* create PAVs here on purpose.

    virtual_ptavs = PTAV_r.browse()  # empty recordset

    # Normalize iterable of cpq values
    CPQV = read_env["cpq.attribute.value"]
    if isinstance(cpq_value_ids, (list, tuple, set)):
        # ints/strs -> browse; records -> keep
        ids = []
        recs = []
        for item in cpq_value_ids:
            if getattr(item, "exists", None):
                recs.append(item)
            else:
                try:
                    ids.append(int(item))
                except Exception:
                    continue
        cpq_vals = (recs and read_env["cpq.attribute.value"].browse([r.id for r in recs])) | (ids and CPQV.browse(ids)) or CPQV.browse()
    else:
        cpq_vals = cpq_value_ids if getattr(cpq_value_ids, "exists", None) else CPQV.browse()

    for cpq_val in cpq_vals:
        if not cpq_val.exists():
            continue

        cpq_attr = cpq_val.attribute_id
        if not cpq_attr or not cpq_attr.exists():
            continue

        # Ensure/resolve a product.attribute for this CPQ attribute (no direct env.sudo)
        product_attr = getattr(cpq_attr, "linked_product_attribute_id", False)
        if not product_attr or not product_attr.exists():
            # try reuse by name (read env)
            product_attr = PATTR_r.search([("name", "=", cpq_attr.name)], limit=1)
            if not product_attr:
                # create attribute (allowed via env_as_sudo if sudo_create=True)
                product_attr = PATTR_c.create({
                    "name": cpq_attr.name,
                    "create_variant": "no_variant",
                })
            # best-effort backlink (ignore failures silently)
            try:
                if "linked_product_attribute_id" in cpq_attr._fields:
                    cpq_val.attribute_id.sudo().write({"linked_product_attribute_id": product_attr.id})
            except Exception:
                pass

        # Lookup existing PAV (do NOT create here; this function is “virtual only”)
        pav = PAV_r.search([
            ("name", "=", cpq_val.name),
            ("attribute_id", "=", product_attr.id),
        ], limit=1)

        # Build ephemeral PTAV (not persisted)
        v = PTAV_r.new({
            "product_tmpl_id": product_tmpl.id,
            "attribute_id": product_attr.id,
            "product_attribute_value_id": pav.id if pav else False,
        })
        # set simple fields directly
        try:
            v.name = cpq_val.name
        except Exception:
            pass
        try:
            v.price_extra = (cpq_val.price_extra or 0.0)
        except Exception:
            pass
        # optional virtual backlink
        if "x_virtual_cpq_id" in v._fields:
            try:
                v.x_virtual_cpq_id = str(cpq_val.id)
            except Exception:
                pass

        virtual_ptavs += v

    return virtual_ptavs

def generate_summary_html(
    summary_rows,
    price_summary=None,
    ptal_ids=None,
    product_name=None,
    quantity=None,
    matrix_override=False,
    qr_data_url=None,
    show_qr=True,
    laterality="bilateral",
):
    _logger.info("[SummaryHTML] Row count = %s", len(summary_rows) if summary_rows else 0)

    def safe(val):
        if val is None:
            return "—"
        if isinstance(val, (int, float)):
            return f"{val:.2f}"
        txt = str(val).strip()
        return txt if txt else "—"

    def render_split_row(row):
        label = safe(row.get("label"))
        left  = safe(row.get("left"))
        right = safe(row.get("right"))
        price = safe(row.get("priceExtra", 0.0))
        match_icon = (
            '<i class="fa fa-check text-success fa-lg" title="Match"></i>'
            if row.get("match") else
            '<i class="fa fa-times text-danger fa-lg" title="Mismatch"></i>'
        )
        return f"""
        <tr>
            <td class="text-start fw-bold">{label}</td>
            <td><span>{left}</span></td>
            <td><span>{right}</span></td>
            <td><i class="fa fa-check text-success fa-lg" title="Split"></i></td>
            <td>{match_icon}</td>
            <td class="text-end"><span>{price}</span>$</td>
        </tr>"""

    def render_one_sided_row(row, which_side):
        label = safe(row.get("label"))
        price = safe(row.get("priceExtra", 0.0))
        left  = safe(row.get("left"))  if which_side == "left"  else "—"
        right = safe(row.get("right")) if which_side == "right" else "—"
        # For non-split one-sided rows, match/split icons are “neutral”
        return f"""
        <tr>
            <td class="text-start fw-bold">{label}</td>
            <td><span>{left}</span></td>
            <td><span>{right}</span></td>
            <td><i class="fa fa-minus text-muted" title="Not split"></i></td>
            <td><i class="fa fa-minus text-muted"></i></td>
            <td class="text-end"><span>{price}</span>$</td>
        </tr>"""

    def render_shared_row(row):
        label  = safe(row.get("label"))
        shared = safe(row.get("shared"))
        price  = safe(row.get("priceExtra", 0.0))
        match_icon = (
            '<i class="fa fa-check text-success fa-lg" title="Match"></i>'
            if row.get("match") else
            '<i class="fa fa-minus text-muted"></i>'
        )
        return f"""
        <tr>
            <td class="text-start fw-bold">{label}</td>
            <td colspan="3"><span>{shared}</span></td>
            <td>{match_icon}</td>
            <td class="text-end"><span>{price}</span>$</td>
        </tr>"""

    # Decide how to render each row
    body_html = []
    for row in (summary_rows or []):
        is_split = bool(row.get("isSplit"))
        if is_split:
            body_html.append(render_split_row(row))
        else:
            if laterality == "left":
                body_html.append(render_one_sided_row(row, "left"))
            elif laterality == "right":
                body_html.append(render_one_sided_row(row, "right"))
            else:
                body_html.append(render_shared_row(row))

    total_price = safe((price_summary or {}).get("total"))

    caption_html = (
        f"""<div class="mb-2 fw-bold">{safe(product_name) or "Configured Product"} — Quantity: {quantity or 1}</div>"""
        if (product_name or quantity) else ""
    )
    qr_html = (
        f"""<div class="text-end mt-2"><img src="{qr_data_url}" alt="QR Code" style="height: 80px;" /></div>"""
        if qr_data_url and show_qr else ""
    )

    return f"""
    <div class="summary-table-wrapper">
        {caption_html}
        <table class="table table-sm table-bordered align-middle text-center mb-0">
            <thead class="table-light">
                <tr>
                    <th>Attribute</th>
                    <th>LT</th>
                    <th>RT</th>
                    <th>Split</th>
                    <th>Match</th>
                    <th>Price</th>
                </tr>
            </thead>
            <tbody>
                {''.join(body_html)}
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="5" class="text-end fw-bold">Total</td>
                    <td class="text-end fw-bold">{total_price}$</td>
                </tr>
            </tfoot>
        </table>
        {qr_html}
    </div>
    """

def strip_fallback_metadata(selected, preferences):
    """
    Return a copy of `selected` with per-side `note` and isPreferred fields **only**
    if they were not introduced by preference fallback logic.
    """
    selected = copy.deepcopy(selected)
    preference_ids = {
        str(ptav["id"])
        for ptal in preferences or []
        for ptav in ptal.get("ptav_ids", [])
    }

    def clean_dict(d, side=None):
        for ptav_id, entry in d.items():
            if ptav_id in preference_ids:
                # Remove both isPreferred and per-side flags for this fallback
                entry.pop("note", None)
                entry.pop("isPreferred", None)
                entry.pop("isPreferredLeft", None)
                entry.pop("isPreferredRight", None)
                if side == "left":
                    entry.pop("noteLeft", None)
                elif side == "right":
                    entry.pop("noteRight", None)

    if "left" in selected and "right" in selected:
        clean_dict(selected["left"], side="left")
        clean_dict(selected["right"], side="right")
        if "shared" in selected:
            clean_dict(selected["shared"])
    else:
        clean_dict(selected)

    return selected

def normalize_grouped_to_selected(config):
    """
    Given a CPQ payload that might have:
      - a top-level selected dict (flat or already split),
      - or grouped / groupedCombinationForBackend,
      - or legacy grouped.selected,
    always return exactly three buckets: left/right/shared,
    scooping any extra keys in `selected` into `shared`.
    """
    # 1️⃣ Try top-level selected first
    sel = config.get("selected", {})
    if isinstance(sel, dict):
        left   = sel.get("left")   or {}
        right  = sel.get("right")  or {}
        shared = sel.get("shared") or {}
        # pick up any other keys into shared
        extra = {k: v for k, v in sel.items() if k not in ("left", "right", "shared")}
        if left or right or shared or extra:
            shared.update(extra)
            return {"left": left, "right": right, "shared": shared}

    # 2️⃣ Fallback to grouped / groupedCombinationForBackend
    grouped = config.get("grouped") or config.get("groupedCombinationForBackend")
    if not isinstance(grouped, dict):
        return {"left": {}, "right": {}, "shared": {}}

    # Already split/shared?
    if all(side in grouped for side in ("left", "right", "shared")):
        top_left   = grouped.get("left")   or {}
        top_right  = grouped.get("right")  or {}
        top_shared = grouped.get("shared") or {}

        # nested-shared shape?
        if isinstance(top_shared, dict) and any(side in top_shared for side in ("left","right","shared")):
            return {
                "left":   top_left or top_shared.get("left", {}),
                "right":  top_right or top_shared.get("right", {}),
                "shared": top_shared.get("shared", {}),
            }

        # simple split
        return {"left": top_left, "right": top_right, "shared": top_shared}

    # legacy grouped.selected
    inner = grouped.get("selected")
    if isinstance(inner, dict):
        return {"left": {}, "right": {}, "shared": inner}

    # give up
    return {"left": {}, "right": {}, "shared": {}}

# def enrich_ptal_ids_with_virtual_ids(odoo_env, ptal_ids, *, company_id=None):
#     """
#     Ensure each value dict under ptal_ids has x_virtual_cpq_id
#     so summary can match CPQ-id keys from selected buckets.

#     ptal_ids: list of attribute dicts each with "values"/"ptav_ids" lists.
#     """
#     odoo_env = ensure_env(odoo_env)
#     if company_id:
#         odoo_env = env_with_context(odoo_env, allowed_company_ids=[company_id])

#     all_ids = []
#     for attr in ptal_ids or []:
#         values = attr.get("values") or attr.get("ptav_ids") or []
#         for v in values:
#             pid = v.get("id")
#             if pid and str(pid).isdigit():
#                 all_ids.append(int(pid))

#     if not all_ids:
#         return ptal_ids

#     PTAV = odoo_env["product.template.attribute.value"]
#     ptav_map = {p.id: (str(p.x_virtual_cpq_id) if getattr(p, "x_virtual_cpq_id", False) else None)
#                 for p in PTAV.browse(list(set(all_ids))).exists()}

#     for attr in ptal_ids or []:
#         values = attr.get("values") or attr.get("ptav_ids") or []
#         for v in values:
#             if not v.get("x_virtual_cpq_id"):
#                 pid = v.get("id")
#                 vid = ptav_map.get(pid)
#                 if vid:
#                     v["x_virtual_cpq_id"] = vid

#     return ptal_ids

def enrich_ptal_ids_with_virtual_ids(odoo_env, ptal_ids):
    """Add x_virtual_cpq_id to each value dict when missing, without changing structure."""
    odoo_env = ensure_env(odoo_env)
    PTAV = odoo_env["product.template.attribute.value"].sudo()

    for attr in ptal_ids or []:
        values = attr.get("values") or attr.get("ptav_ids") or []
        for v in values:
            if isinstance(v, dict) and not v.get("x_virtual_cpq_id"):
                pid = v.get("ptav_id") or v.get("id")  # prefer explicit ptav_id if you kept it
                if pid and isinstance(pid, int):
                    ptav = PTAV.browse(pid)
                    if ptav.exists() and getattr(ptav, "x_virtual_cpq_id", False):
                        v["x_virtual_cpq_id"] = str(ptav.x_virtual_cpq_id)
    return ptal_ids


def render_summary_html(odoo_env, order_line, config):
    """
    Render a CPQ configuration summary table for a sale.order.line.

    Fixes:
      • Left-only / Right-only rows no longer show up as shared/blank.
      • Non-split rows respect laterality when deciding how to render.
    """
    
    odoo_env = ensure_env(odoo_env, order_line)
    if getattr(order_line, "company_id", False):
        odoo_env = env_with_context(odoo_env, allowed_company_ids=[order_line.company_id.id])

        # odoo_env = odoo_env.with_context(allowed_company_ids=[order_line.company_id.id])
    
    
    # 1) Validate order_line
    if not order_line or getattr(order_line, "_name", "") != "sale.order.line":
        _logger.warning("[SummaryHTML] Called without a sale.order.line; rendering preview only.")
    else:
        _logger.debug("[SummaryHTML] render_summary_html order_line=%s", order_line.id)

    # 2) Ensure dict input
    if isinstance(config, str):
        try:
            config = json.loads(config)
        except Exception:
            _logger.warning("[SummaryHTML] Invalid JSON; using empty config.")
            config = {}

    # 3) Canonicalize and normalize
    config = get_cpq_config_dict(config)
    config["selected"] = normalize_selected_values(config.get("selected", {}))
    config["selected"] = normalize_selected_keys(config["selected"])

    grouped     = config.get("grouped") or config.get("groupedCombinationForBackend")
    ptal_ids    = config.get("ptal_ids") or []
    split_map   = config.get("splitByAttrMap", {}) or {}
    laterality  = config.get("laterality", "bilateral")
    quantity    = config.get("quantity_to_make", 1)

    # If grouped present with content, prefer it
    if isinstance(grouped, dict) and any(grouped.get(s) for s in ("left", "right", "shared")):
        config["selected"] = {
            "left":   grouped.get("left",   {}) or {},
            "right":  grouped.get("right",  {}) or {},
            "shared": grouped.get("shared", {}) or {},
        }
        config["selected"] = normalize_selected_values(config["selected"])
        config["selected"] = normalize_selected_keys(config["selected"])

    # Patch split map from grouped.shared when missing
    if not split_map:
        derived = {}
        gshared = (grouped or {}).get("shared", {}) if isinstance(grouped, dict) else {}
        if isinstance(gshared, dict):
            for side in ("left", "right"):
                for pid in (gshared.get(side) or {}):
                    for a in ptal_ids:
                        for v in a.get("ptav_ids") or a.get("values") or []:
                            if str(v.get("id")) == str(pid) or str(v.get("x_virtual_cpq_id")) == str(pid):
                                derived[str(a["id"])] = True
        if derived:
            split_map = derived
            config["splitByAttrMap"] = derived

    # If nothing in selected, fall back to grouped.shared
    used_grouped_shared = False
    if not (config["selected"].get("left") or config["selected"].get("right") or config["selected"].get("shared")):
        gshared = (grouped or {}).get("shared", {})
        if gshared:
            config["selected"] = {"left": {}, "right": {}, "shared": dict(gshared)}
            config["selected"] = normalize_selected_values(config["selected"])
            config["selected"] = normalize_selected_keys(config["selected"])
            used_grouped_shared = True

    # Flatten legacy shapes (only if we didn’t just lift grouped.shared)
    def _needs_flat(sel):
        return any(not isinstance(v, dict)
                   for side in ("left", "right", "shared")
                   for v in (sel.get(side) or {}).values())

    if not used_grouped_shared and _needs_flat(config["selected"]):
        flat = flatten_grouped_selection(grouped or {})
        rebuilt = split_selected_dict_by_attribute(flat, ptal_ids, split_map, laterality)
        config["selected"] = normalize_selected_keys(normalize_selected_values(rebuilt))
        _logger.info("[SplitByAttr] Rebuilt selected from grouped fallback.")
    else:
        _logger.info("[SplitByAttr] Using existing left/right/shared selection.")

    # 4) Pricing + QR
    breakdown = compute_cpq_price_breakdown(odoo_env, order_line, config)
    matrix_override = bool(breakdown.get("from_matrix"))
    qr_data_url = generate_cpq_order_qr_payload(getattr(order_line, "order_id", None)) if hasattr(order_line, "order_id") else None

    # 5) Structure guard
    structured = determine_selected_structure(config["selected"])
    if any(isinstance(v, dict) and ("left" in v or "right" in v) for v in structured.values()):
        _logger.error("[SummaryHTML] Nested left/right structure detected; aborting.")
        return "<div class='text-danger'>Invalid configuration structure</div>"

    for side in ("left", "right", "shared"):
        structured.setdefault(side, {})

    # 6) Strip fallback (UI) metadata
    prefs = config.get("cpqPreferences", [])
    config["selected"] = normalize_selected_keys(normalize_selected_values(strip_fallback_metadata(structured, prefs)))

    # 7) Defensive fan‑out only for bilateral split (not for left/right)
    if (
        config.get("split") is True and
        laterality == "bilateral" and
        not config["selected"].get("left") and
        not config["selected"].get("right") and
        config["selected"].get("shared")
    ):
        config["selected"]["left"]  = dict(config["selected"]["shared"])
        config["selected"]["right"] = dict(config["selected"]["shared"])
        config["selected"]["shared"] = {}

    # 8) Nothing selected?
    if not (config["selected"].get("left") or config["selected"].get("right") or config["selected"].get("shared")):
        return Markup("""
            <div class='alert alert-warning'>
                No attribute selections were available for this configuration. Please edit the line and reconfigure.
            </div>
        """)

    # 9) Final canonicalization and rows
    has_split_attrs = any(split_map.get(str(a.get("id"))) for a in ptal_ids)
    config["split"] = has_split_attrs
    selected_final = canonicalize_selected_buckets(config["selected"], config["split"], laterality)
    
    # ...existing...
    has_split_attrs = any(split_map.get(str(a.get("id"))) for a in ptal_ids)
    config["split"] = has_split_attrs
    selected_final = canonicalize_selected_buckets(config["selected"], config["split"], laterality)

    # --- KEEP SPLIT ATTRS SPLIT EVEN IF LT == RT (fan-out shared to both sides) ---
    if laterality == "bilateral" and has_split_attrs:
        sel = selected_final or {}
        sel.setdefault("left", {})
        sel.setdefault("right", {})
        sel.setdefault("shared", {})

        for a in (ptal_ids or []):
            aid = str(a.get("id"))
            if not split_map.get(aid):
                continue  # not a split attribute

            # Collect all PTAV ids for this attribute (support legacy shapes)
            pts = (a.get("ptav_ids") or a.get("values") or [])
            ptav_ids = []
            for v in pts:
                if isinstance(v, dict):
                    pid = v.get("id") or v.get("x_virtual_cpq_id")
                else:
                    pid = v  # id or [id, name]
                    if isinstance(pid, (list, tuple)):
                        pid = pid[0]
                if pid is not None:
                    ptav_ids.append(str(pid))

            # If a split attribute's choice lives in shared, copy it to both sides
            for pid in ptav_ids:
                if pid in sel["shared"]:
                    val = sel["shared"].pop(pid)
                    sel["left"].setdefault(pid, val)
                    sel["right"].setdefault(pid, val)

        selected_final = sel
    # ------------------------------------------------------------------------------
    company_id = order_line.company_id.id if getattr(order_line, "company_id", False) else None
    ptal_ids = enrich_ptal_ids_with_virtual_ids(odoo_env, ptal_ids, company_id=company_id)

    rows = build_summary({
        "selected": selected_final,
        "ptal_ids": ptal_ids,
        "split": config.get("split", False),
        "splitByAttrMap": split_map,
        "laterality": laterality,
        "quantity_to_make": quantity,
    })

    # 10) Render HTML (laterality-aware)
    return generate_summary_html(
        summary_rows=rows,
        price_summary={
            "base": breakdown.get("base_price", 0.0),
            "extrasSubtotal": breakdown.get("extras_total", 0.0),
            "total": breakdown.get("total", 0.0),
        },
        ptal_ids=ptal_ids,
        product_name=getattr(order_line.product_template_id, "name", "Configured Product"),
        quantity=quantity,
        matrix_override=matrix_override,
        qr_data_url=qr_data_url,
        show_qr=False,
        laterality=laterality,  # <- important: lets the renderer show LT/RT properly when non-split
    )

def determine_selected_structure(raw_selected):
    if not isinstance(raw_selected, dict):
        _logger.warning("Invalid selected format (not a dict): %s", type(raw_selected))
        return {}

    if "left" in raw_selected or "right" in raw_selected:
        return {
            "left": raw_selected.get("left", {}),
            "right": raw_selected.get("right", {}),
            "shared": raw_selected.get("shared", {}),
        }

    # If we reach here, it's a flat structure — normalize to bilateral shared
    rebuilt = {}
    for ptav_id, val in list(raw_selected.items()):
        if isinstance(val, dict) and "value" in val:
            # Map legacy isPreferred to both sides, if present
            entry = dict(val)
            if entry.get("isPreferred") is not None:
                entry["isPreferredLeft"] = entry["isPreferred"]
                entry["isPreferredRight"] = entry["isPreferred"]
                entry.pop("isPreferred")
            rebuilt[ptav_id] = entry
        elif isinstance(val, (str, int)):  # only allow primitive value -> wrap
            rebuilt[ptav_id] = {
                "id": ptav_id,
                "value": val,
                "isPreferredLeft": False,
                "isPreferredRight": False,
            }
        else:
            _logger.warning("[‼] Ignoring malformed selected value for PTAV %s: %r", ptav_id, val)

    _logger.info("Flattened selected detected — converting to bilateral shared")
    # Always include 'shared' for robust structure
    return {
        "left": copy.deepcopy(rebuilt),
        "right": copy.deepcopy(rebuilt),
        "shared": {},
    }

def render_summary_plaintext(odoo_env, order, config):
    # odoo_env = ensure_env(odoo_env, order)
    # if getattr(order, "company_id", False):
    #     odoo_env = odoo_env.with_context(allowed_company_ids=[order.company_id.id])
    odoo_env = ensure_env(odoo_env, order)
    if getattr(order, "company_id", False):
        odoo_env = env_with_context(odoo_env, allowed_company_ids=[order.company_id.id])
    html = render_summary_html(odoo_env, order, config)
    return Markup(html).striptags()

def _pick_selected(cfg):
    grouped = cfg.get("grouped") or {}
    selected = cfg.get("selected") or {}

    has_grouped = any((grouped.get(k) or {}) for k in ("left", "right", "shared"))
    has_selected = any((selected.get(k) or {}) for k in ("left", "right", "shared"))

    if has_grouped:
        return grouped
    if has_selected:
        return selected
    return rebuild_selected_dict(cfg)

def compute_cpq_price_breakdown(odoo_env, order_line, config):
    """Return a pricing breakdown for a CPQ-configured sale.order.line."""

    odoo_env = ensure_env(odoo_env, order_line, getattr(order_line, "product_template_id", None))
    if getattr(order_line, "company_id", False):
        odoo_env = env_with_context(odoo_env, allowed_company_ids=[order_line.company_id.id])

    # ------------------------ helpers ------------------------
    def _default_breakdown(ptavs=None, laterality="bilateral", qty=1):
        return {
            "base_price": 0.0,
            "discount_factor": 1.0,
            "quantity": qty,
            "laterality": laterality,
            "left": 0.0,
            "right": 0.0,
            "extras_total": 0.0,
            "subtotal": 0.0,
            "final_price": 0.0,
            "total": 0.0,
            "from_matrix": False,
            "ptal_ids": ptavs or [],
        }

    def _normalize_config(raw):
        """
        Parse any incoming shape → canonical CPQ config dict
        with a 'selected' that has left/right/shared OR a grouped fallback.
        """
        cfg = get_cpq_config_dict(raw) if isinstance(raw, (dict, str)) else {}
        if not isinstance(cfg, dict):
            return {}

        # Pick the proper selection structure
        selected = _pick_selected(cfg)
        
        # Strip any UI-only metadata from the chosen selection
        prefs = cfg.get("cpqPreferences", [])
        clean_selected = strip_fallback_metadata(selected, prefs)
        cfg["selected"] = clean_selected
        return cfg

    def _extract_ptavs(product_tmpl, selected_dict):
        ptavs, _custom_dict, _sel = extract_cpq_ptavs(product_tmpl.env, product_tmpl, selected_dict)
        real_ids = [p.id for p in ptavs if p.id and not isinstance(p.id, NewId)]
        if not ptavs:
            _logger.warning("[Custom] No PTAVs generated. Summary will be empty.")
        for p in ptavs:
            _logger.debug(" - %s (ID: %s, price_extra=%.2f, virtual=%s)",
                        p.name, p.id, p.price_extra, isinstance(p.id, NewId))
        return ptavs, real_ids

    # near the top of compute_cpq_price_breakdown
    _cpq_price_cache = {}
    def _cpq_price_for_ptav(p):
        # prefer CPQ value price if we can resolve it
        vid = getattr(p, "x_virtual_cpq_id", False)
        if vid:
            if vid in _cpq_price_cache:
                return _cpq_price_cache[vid]
            try:
                cpqv = odoo_env["cpq.attribute.value"].sudo().browse(int(vid))
                if cpqv.exists():
                    _cpq_price_cache[vid] = float(cpqv.price_extra or 0.0)
                    return _cpq_price_cache[vid]
            except Exception:
                pass
        return float(getattr(p, "price_extra", 0.0) or 0.0)



    def _lookup_matrix_price(product_tmpl, real_ptav_ids, qty, currency):
        """Try cpq.price.matrix on subset match; return (price_total or None)."""
        matrices = odoo_env["cpq.price.matrix"].sudo().search([("product_tmpl_id", "=", product_tmpl.id)])
        if not matrices:
            return None
        # any matrix whose PTAV set is subset of the selected ids
        match = matrices.filtered(lambda m: set(m.ptav_ids.ids).issubset(set(real_ptav_ids)))
        if not match:
            return None
        matrix_price = match[0].price_total  # first match wins
        return currency.round(matrix_price * qty)

    def _side_totals(ptavs, selected, laterality, split):
        def _has(bucket, pid):
            return pid in (selected.get(bucket) or {})

        def _pid(p):
            return str(getattr(p, "x_virtual_cpq_id", p.id))

        left_total = right_total = 0.0

        if laterality == "bilateral":
            if split:
                for p in ptavs:
                    pid = _pid(p)
                    pe = _cpq_price_for_ptav(p)
                    if _has("left", pid):
                        left_total += pe
                    if _has("right", pid):
                        right_total += pe
            else:
                shared = 0.0
                for p in ptavs:
                    pid = _pid(p)
                    if _has("shared", pid):
                        shared += _cpq_price_for_ptav(p)
                left_total = right_total = shared
        elif laterality == "left":
            for p in ptavs:
                pid = _pid(p)
                if _has("left", pid) or _has("shared", pid):
                    left_total += _cpq_price_for_ptav(p)
        elif laterality == "right":
            for p in ptavs:
                pid = _pid(p)
                if _has("right", pid) or _has("shared", pid):
                    right_total += _cpq_price_for_ptav(p)
        else:
            for p in ptavs:
                pid = _pid(p)
                pe = _cpq_price_for_ptav(p)
                if _has("shared", pid):
                    left_total += pe
                    right_total += pe
                elif _has("left", pid):
                    left_total += pe
                elif _has("right", pid):
                    right_total += pe
        return left_total, right_total

    # ------------------------ validation ------------------------
    if not order_line or not hasattr(order_line, "product_template_id"):
        _logger.warning("[CPQ] Missing or invalid order_line")
        return _default_breakdown()

    if not isinstance(config, (dict, str)) or not config:
        _logger.warning("[CPQ] Missing or invalid config, returning default breakdown.")
        return _default_breakdown()

    product_tmpl = order_line.product_template_id
    partner = order_line.order_id.partner_id if order_line.order_id else odoo_env.user.partner_id
    currency = (order_line.currency_id or odoo_env.user.company_id.currency_id).ensure_one()

    # ------------------------ config ------------------------
    cfg = _normalize_config(config)
    if not cfg:
        _logger.warning("[CPQ] Could not parse config_dict, returning default breakdown.")
        return _default_breakdown()

    qty        = int(cfg.get("quantity_to_make", 1) or 1)
    laterality = cfg.get("laterality", "bilateral")
    split      = bool(cfg.get("split", False))
    selected   = cfg.get("selected") or {}

    # PTAVs (and real ids for matrix)
    ptavs, real_ptav_ids = _extract_ptavs(product_tmpl, selected)

    # ------------------------ matrix ------------------------
    matrix_final = _lookup_matrix_price(product_tmpl, real_ptav_ids, qty, currency)
    if matrix_final is not None:
        _logger.info(
            "[CPQ] Breakdown (matrix): base=0.00, extras=0.00, subtotal=%0.2f, total=%0.2f, split=%s, laterality=%s",
            matrix_final / qty if qty else 0.0, matrix_final, split, laterality
        )
        return {
            "base_price": 0.0,
            "discount_factor": 1.0,
            "quantity": qty,
            "laterality": laterality,
            "left": 0.0,
            "right": 0.0,
            "extras_total": 0.0,
            "subtotal": matrix_final,   # per unit subtotal not meaningful in matrix; keep total as subtotal for clarity
            "final_price": matrix_final,
            "total": matrix_final,
            "from_matrix": True,
            "ptal_ids": ptavs,
        }

    # ------------------------ compute base & extras ------------------------
    base_price = float(product_tmpl.list_price or 0.0)
    base_mult  = 2 if laterality == "bilateral" else 1
    discount   = get_partner_discount(odoo_env, partner, product_tmpl)  # e.g., 1.0 → no change
    discounted_base_per_pair = base_price * base_mult * discount

    left_pp, right_pp = _side_totals(ptavs, selected, laterality, split)  # per-pair
    extras_pp = left_pp + right_pp
    subtotal_pp = discounted_base_per_pair + extras_pp

    # apply quantity once
    final_price = currency.round(subtotal_pp * qty)
    left_q      = round(left_pp * qty, 2)
    right_q     = round(right_pp * qty, 2)
    extras_q    = round(extras_pp * qty, 2)
    subtotal_q  = round(subtotal_pp * qty, 2)

    _logger.info(
        "[CPQ] Breakdown: base=%0.2f, left=%0.2f, right=%0.2f, extras=%0.2f, subtotal=%0.2f, total=%0.2f, split=%s, laterality=%s",
        base_price, left_q, right_q, extras_q, subtotal_q, final_price, split, laterality
    )

    return {
        "base_price": round(base_price * base_mult, 2),  # pre-discount, per pair
        "discount_factor": discount,
        "quantity": qty,
        "laterality": laterality,
        "left": left_q,
        "right": right_q,
        "extras_total": extras_q,
        "subtotal": subtotal_q,
        "final_price": final_price,
        "total": final_price,
        "from_matrix": False,
        "ptal_ids": ptavs,
    }

def get_partner_discount(odoo_env, partner, template):
    # odoo_env = ensure_env(odoo_env, partner)
    # if getattr(partner, "company_id", False):
    #     odoo_env = odoo_env.with_context(allowed_company_ids=[partner.company_id.id])
    odoo_env = ensure_env(odoo_env, partner)
    if getattr(partner, "company_id", False):
        odoo_env = env_with_context(odoo_env, allowed_company_ids=[partner.company_id.id])
        
    # Expand this to support: pricelists, tags, partner categories, volume tiers, custom partner fields (e.g., partner.cpq_discount_pct)
    if not partner:
        return 1.0 # No discount

    # Example rule: VIP partners get 10% off
    if partner.name == "VIP Partner":
        return 0.9

    # Future: implement customer category discounting
    return 1.0

def sanitize_for_json(value, depth=0, max_depth=20):
    """Recursively sanitize Python or Odoo objects for JSON serialization, including ID and name when present."""
    if depth > max_depth:
        return "..."

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, (Date, Datetime)):
        return str(value)

    if isinstance(value, BaseModel):
        if not value:
            return None
        if len(value) == 1:
            return {"id": value.id, "name": value.display_name or value.name or str(value)}
        return [{"id": rec.id, "name": rec.display_name or rec.name or str(rec)} for rec in value]

    if isinstance(value, dict):
        return {
            sanitize_for_json(k, depth + 1): sanitize_for_json(v, depth + 1)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [sanitize_for_json(v, depth + 1) for v in value]

    if hasattr(value, "id"):
        try:
            return {"id": value.id, "name": getattr(value, "display_name", str(value))}
        except Exception:
            return str(value)

    return str(value)

def generate_cpq_qr_payload(order_id, line_id, product_template_id, config_hash=None, version=1):
    """
    Returns a canonical QR payload URI for a CPQ-configured sale order line.
    Format: cpq://order/{order_id}/line/{line_id}/template/{product_template_id}?config={hash}&version=1
    This will return values like: cpq://order/1001/line/203/template/45?config=abc123&version=1
    """
    base_uri = f"cpq://order/{order_id}/line/{line_id}/template/{product_template_id}"
    query_params = {}
    if config_hash:
        query_params["config"] = config_hash
    if version:
        query_params["version"] = str(version)
    if query_params:
        return f"{base_uri}?{urllib.parse.urlencode(query_params)}"
    return base_uri

def generate_cpq_order_qr_payload(order):
    """
    Generate a CPQ order-level QR payload string (URI-style with base64-encoded JSON).

    Args:
        order (recordset): A single sale.order record

    Returns:
        str: QR payload string like cpq://order?data=<base64>
    """
    if not order or not order.id:
        return None

    try:
        payload = {
            "type": "cpq_order",
            "version": 1,
            "order_id": order.id,
            "customer": order.partner_id.name or "",
            "date": str(order.date_order.date() if order.date_order else fields.Date.today()),
            "lines": []
        }

        for line in order.order_line:
            if not line.product_template_id.cpq_ok or not line.cpq_config_hash:
                continue

            payload["lines"].append({
                "line_id": line.id,
                "template_id": line.product_template_id.id,
                "product_name": line.name or "",
                "config_hash": line.cpq_config_hash,
                "quantity": line.product_uom_qty,
            })

        encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
        return f"cpq://order?data={encoded}"
    except Exception as e:
        _logger.warning("Failed to generate CPQ order QR payload: %s", e)
        return None

def flatten_grouped_selection(grouped):
    """
    Flatten a grouped selection structure to a flat selected dict.
    Supports left/right split structures or grouped.selected.
    Returns a dict keyed by PTAV IDs as ints, with metadata as values.
    """
    if not grouped or not isinstance(grouped, dict):
        return {}

    # 1. If "selected" is a key, this is already a flat selection
    if "selected" in grouped and isinstance(grouped["selected"], dict):
        return grouped["selected"]

    # 2. If "left" or "right" keys are present, merge them
    if "left" in grouped or "right" in grouped:
        flat = {}
        left_dict = grouped.get("left", {}) or {}
        right_dict = grouped.get("right", {}) or {}
        all_keys = set(left_dict.keys()) | set(right_dict.keys())
        for ptav_id in all_keys:
            try:
                int_ptav_id = int(ptav_id)
            except (TypeError, ValueError):
                continue  # Skip non-integer keys
            left_val = left_dict.get(ptav_id, {})
            right_val = right_dict.get(ptav_id, {})
            merged = {**left_val, **right_val}
            if merged:
                flat[int_ptav_id] = merged
        return flat

    # 3. Already a flat dict (no left/right/selected), so just filter numeric keys
    return {
        int(k): v
        for k, v in grouped.items()
        if str(k).isdigit()
    }

def partition_grouped_shared_to_selected(shared, ptal_ids):
    """
    Partition a grouped.shared dict into selected.left/right/shared.
    Each attribute in ptal_ids will assign up to one value to left and one to right.
    """
    left, right, shared_out = {}, {}, {}

    # Build attribute->list of value dicts from shared (order preserved)
    attr_val_map = {}
    value_to_attr = {}
    for attr in ptal_ids:
        aid = str(attr["id"])
        attr_val_map[aid] = []
        for val in attr.get("values", []):
            vid = str(val["id"])
            value_to_attr[vid] = aid

    # Populate attr_val_map: group all shared values by attribute
    for vid, meta in (shared or {}).items():
        aid = value_to_attr.get(str(vid))
        if aid:
            attr_val_map[aid].append(meta)

    # For each attribute, assign the first to left, the second to right (if present)
    for aid, vals in attr_val_map.items():
        if not vals:
            continue
        if len(vals) == 1:
            left[str(vals[0]["id"])] = vals[0]
        elif len(vals) >= 2:
            _logger.warning("[CPQ] Attribute %s has >2 values in grouped.shared: %s", aid, vals)
            left[str(vals[0]["id"])] = vals[0]
            right[str(vals[1]["id"])] = vals[1]
        # If more than 2, junk extra values (or put in shared_out, up to you)
        # for v in vals[2:]:
        #     shared_out[str(v["id"])] = v

    return {"left": left, "right": right, "shared": shared_out}

def canonicalize_cpq_config(config):
    """
    Normalize CPQ config so 'selected' always has left/right/shared buckets.

    - Bilateral + split: if only grouped.shared present, partition into left/right.
    - Bilateral + shared: if only grouped.shared present, copy to selected.shared.
    - Unilateral (left/right): if buckets empty but grouped.shared present, move that shared into the active side.
    """
    # 1) Parse if a JSON string was passed
    cfg = {}
    if isinstance(config, (str, bytes)):
        try:
            cfg = json.loads(config)
        except Exception:
            # fall through to defaults below
            cfg = {}
    elif isinstance(config, dict):
        cfg = dict(config)  # shallow copy
    else:
        cfg = {}

    # 2) Core flags
    laterality = (cfg.get("laterality") or "bilateral").strip().lower()
    split = bool(cfg.get("split", False))

    # 3) Ensure both shapes exist with 3 buckets each
    selected_in = cfg.get("selected") or {}
    grouped_in  = cfg.get("grouped") or {}

    selected = {
        "left":   dict(selected_in.get("left")   or {}),
        "right":  dict(selected_in.get("right")  or {}),
        "shared": dict(selected_in.get("shared") or {}),
    }
    grouped = {
        "left":   dict(grouped_in.get("left")   or {}),
        "right":  dict(grouped_in.get("right")  or {}),
        "shared": dict(grouped_in.get("shared") or {}),
    }

    grouped_shared = grouped["shared"]

    # 4) Unilateral: shared => active side; never split
    if laterality in ("left", "right"):
        active = laterality
        # nothing selected anywhere, but we have grouped.shared → move it
        if not selected["left"] and not selected["right"] and not selected["shared"] and grouped_shared:
            selected[active] = dict(grouped_shared)
            grouped["shared"] = {}
        # if caller stuffed unilateral under shared, move to active side
        if selected["shared"] and not selected[active]:
            selected[active] = dict(selected["shared"])
            selected["shared"] = {}
        split = False

    else:
        # 5) Bilateral
        if split:
            # split grouped.shared only when left/right empty
            if grouped_shared and not selected["left"] and not selected["right"]:
                # make sure this helper is imported from your helper module
                new_sel = partition_grouped_shared_to_selected(grouped_shared, cfg.get("ptal_ids", []) or [])
                selected["left"]   = dict(new_sel.get("left")   or {})
                selected["right"]  = dict(new_sel.get("right")  or {})
                selected["shared"] = dict(new_sel.get("shared") or {})
                grouped["shared"] = {}
        else:
            # shared bilateral: just copy grouped.shared → selected.shared if nothing else selected
            if grouped_shared and not selected["left"] and not selected["right"] and not selected["shared"]:
                selected["shared"] = dict(grouped_shared)
                grouped["shared"] = {}

    # 6) Write back normalized config
    cfg["laterality"] = "left" if laterality == "left" else "right" if laterality == "right" else "bilateral"
    cfg["split"] = split
    cfg["selected"] = selected
    cfg["grouped"] = grouped
    return cfg

def canonicalize_selected_buckets(selected, split, laterality):
    """
    Normalize selected buckets without ever collapsing the whole 'selected' dict
    into a single side. Promote 'shared' into the active side for unilateral
    laterality if that side is empty.
    """
    selected = selected or {}
    left   = dict(selected.get("left")   or {})
    right  = dict(selected.get("right")  or {})
    shared = dict(selected.get("shared") or {})

    if laterality == "left":
        # If nothing explicitly in left, but shared exists, treat as left.
        if not left and shared:
            left, shared = shared, {}
        right = {}  # force empty
    elif laterality == "right":
        if not right and shared:
            right, shared = shared, {}
        left = {}   # force empty
    else:
        # Bilateral
        if split:
            # In split mode, if only shared is provided, fan it out to both.
            if not left and not right and shared:
                left  = dict(shared)
                right = dict(shared)
                shared = {}
        else:
            # Shared bilateral (default): ensure left/right empty, keep shared
            left = {}
            right = {}

    return {"left": left, "right": right, "shared": shared}

def parse_cpq_json(config):
    """Always parse string/dict to a dict for CPQ config."""
    if not config:
        return {}
    if isinstance(config, str):
        try:
            return json.loads(config)
        except Exception:
            return {}
    return config

# --- Backward-compatible resolver: can be called as
def resolve_cpq_value_from_ptav(ptav, env=None):
    """
    Best-effort map from PTAV -> cpq.attribute.value.
    Returns a cpq.attribute.value recordset (possibly empty).
    Accepts:
      - ptav: product.template.attribute.value record
      - env:  optional odoo env; if omitted, will use ptav.env
    """
    if ptav is None:
        return (env or getattr(ptav, "env", None))["cpq.attribute.value"].browse() if env or getattr(ptav, "env", None) else []

    # normalize env
    _env = env or getattr(ptav, "env", None)
    if _env is None:
        # last resort: try to pull from the PAV
        pav = getattr(ptav, "product_attribute_value_id", False)
        _env = getattr(pav, "env", None)
    if _env is None:
        # cannot proceed safely
        return []

    CPQV = _env["cpq.attribute.value"].sudo()

    # 0) backlink via x_virtual_cpq_id on PTAV (fast path)
    if "x_virtual_cpq_id" in ptav._fields:
        vid = (ptav.x_virtual_cpq_id or "").strip() if ptav.x_virtual_cpq_id else False
        if vid and vid.isdigit():
            hit = CPQV.browse(int(vid))
            if hit.exists():
                return hit

    pav = ptav.product_attribute_value_id
    if not pav or not pav.exists():
        return CPQV.browse()

    # 1) primary: match by (attribute, linked_option_id)
    dom = [("attribute_id.linked_product_attribute_id", "=", pav.attribute_id.id)]
    if hasattr(pav, "linked_option_id") and pav.linked_option_id:
        hit = CPQV.search(dom + [("linked_option_id", "=", pav.linked_option_id.id)], limit=1)
        if hit:
            return hit

    # 2) fallback by name (same attribute)
    hit = CPQV.search(dom + [("name", "=", pav.name)], limit=1)
    if hit:
        return hit

    # 3) reverse link occasionally present
    if "linked_product_attribute_value_id" in CPQV._fields:
        hit = CPQV.search([("linked_product_attribute_value_id", "=", pav.id)], limit=1)
        if hit:
            return hit

    return CPQV.browse()

# Optional: model-style wrapper for code that calls self.resolve_cpq_value_from_ptav(ptav)
def resolve_cpq_value_from_ptav_model(self, ptav):
    return resolve_cpq_value_from_ptav(ptav, env=self.env)


