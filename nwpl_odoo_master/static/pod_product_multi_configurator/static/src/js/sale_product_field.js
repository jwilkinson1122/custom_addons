/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { serializeDateTime } from "@web/core/l10n/dates";
import { useService } from "@web/core/utils/hooks";
import { ProductConfiguratorDialog } from "@sale_product_configurator/js/product_configurator_dialog/product_configurator_dialog";
import { x2ManyCommands } from "@web/core/orm_service";

/* ---------- small, safe debug helpers ---------- */

function safePreview(v) {
  try {
    if (v && typeof v === "object") {
      // don’t stringify RelationalModel proxies (circular)
      if (v.model || v.records || v._commands) return "<datapoint>";
    }
    return JSON.stringify(v);
  } catch {
    return "<unserializable>";
  }
}

function shapeOf(v) {
  if (v === null || v === undefined) return String(v);
  if (Array.isArray(v)) {
    if (v[0] && typeof v[0] === "object" && "type" in v[0]) return "x2many-commands";
    if (v.length === 2 && typeof v[0] === "number" && typeof v[1] === "string") return "many2one-tuple";
    return `array(len=${v.length})`;
  }
  return typeof v;
}

function canSet(record, field) {
  // allow if field is in active fields or at least declared on the model
  return !!(record?.activeFields?.[field] || record?.model?._config?.fields?.[field]);
}

function wrapUpdate(record, tag = "REC") {
  if (record.__wrappedUpdate) return;
  const orig = record.update.bind(record);
  record.update = async (vals) => {
    console.group(`[${tag}] record.update`);
    console.table(
      Object.entries(vals).map(([k, v]) => ({
        field: k,
        shape: shapeOf(v),
        preview: safePreview(v),
      }))
    );
    console.groupEnd();
    try {
      return await orig(vals);
    } catch (e) {
      console.error(`[${tag}] batch update failed → probing fields`, e);
      for (const [k, v] of Object.entries(vals)) {
        try {
          console.log(`[${tag}] probe`, k, "→", shapeOf(v), safePreview(v));
          await orig({ [k]: v });
          console.log(`[${tag}] ✓ ok`, k);
        } catch (fe) {
          console.error(`[${tag}] ✗ fail`, k, fe);
        }
      }
      throw e;
    }
  };
  record.__wrappedUpdate = true;
}

/* ---------- main helpers ---------- */

function buildCustomAttributeCmds(product) {
  // Always start with a clear (as Odoo’s own code does)
  const cmds = [x2ManyCommands.set([])];
  for (const ptal of product.attribute_lines || []) {
    const candidate = (ptal.attribute_values || []).find(
      (ptav) => ptav.is_custom && (ptal.selected_attribute_value_ids || []).includes(ptav.id)
    );
    if (candidate) {
      cmds.push(
        x2ManyCommands.create(undefined, {
          custom_product_template_attribute_value_id: [candidate.id, "x"],
          custom_value: ptal.customValue,
        })
      );
    }
  }
  return cmds;
}

function buildNoVariantIds(product) {
  const base = (product.attribute_lines || [])
    .filter((l) => l.create_variant === "no_variant")
    .flatMap((l) => l.selected_attribute_value_ids || [])
    .map(Number);
  const extra = (product.no_variant_extra_ids || []).map(Number);
  return Array.from(new Set([...(base || []), ...(extra || [])]));
}

/* helpers (add near the top of the file) */
function m2oId(v) { return Array.isArray(v) ? Number(v[0] || 0) : Number(v || 0); }

function extractVariantTuple(p) {
  const candidates = [
    m2oId(p.product_id),
    m2oId(p.product_product_id),
    Number(p._variant_id || 0),
    Number(p.variant_id || 0),
  ].filter((x) => Number.isInteger(x) && x > 0);
  const id = candidates[0] || 0;
  if (!id) return null;
  const name = p.display_name || p.name || "Product";
  return [id, name];
}

async function ensureVariantTuple(orm, product, fallbackProductId) {
  // 1) direct from payload
  const t0 = extractVariantTuple(product);
  if (t0) return t0;

  // 2) template’s default/only variant
  const tmplId = Number(product.product_tmpl_id || product.product_template_id || 0);
  if (tmplId) {
    try {
      const [tmpl] = await orm.read("product.template", [tmplId], ["product_variant_id", "name"]);
      const vid = Array.isArray(tmpl?.product_variant_id) ? tmpl.product_variant_id[0] : tmpl?.product_variant_id;
      if (vid) {
        const name = product.display_name || product.name || tmpl?.name || "Product";
        return [vid, name];
      }
    } catch (_) { /* ignore */ }
  }

  // 3) keep the existing line’s product (edit case)
  if (fallbackProductId) {
    const name = product.display_name || product.name || "Product";
    return [fallbackProductId, name];
  }

  return null;
}



async function applyProduct(record, product, tag = "SOL") {
  // x2manys
  const noVariantIds  = buildNoVariantIds(product);
  const noVariantCmds = [x2ManyCommands.set(noVariantIds)];
  const customCmds    = buildCustomAttributeCmds(product);

  // ---- 1) product + attributes (+ laterality) first ----
  // ---- 1) product + attributes (+ laterality) first ----
  const tuple = extractVariantTuple(product);
  const vals1 = {
    // only set when we truly have a valid id → avoids quick-create
    ...(tuple ? { product_id: tuple } : {}),
    product_no_variant_attribute_value_ids: [x2ManyCommands.set(buildNoVariantIds(product))],
    product_custom_attribute_value_ids: buildCustomAttributeCmds(product),
  };
  if (product.laterality_mode && canSet(record, "laterality_mode")) {
    vals1.laterality_mode = product.laterality_mode;
  }
  if (product.laterality_payload && canSet(record, "laterality_payload")) {
    vals1.laterality_payload = product.laterality_payload;
  }

  wrapUpdate(record, tag);
  await record.update(vals1);

  // 2) now set Pair(s) UoM + qty (so product_uom isn't clobbered by _compute_product_uom)
  if (product.product_uom) {
    const uomTuple = Array.isArray(product.product_uom)
      ? product.product_uom
      : [product.product_uom, "Pairs"];
    const qty = ("product_uom_qty" in product)
      ? Number(product.product_uom_qty || 1)
      : Number(product.quantity || 1) || 1;

    // clear packaging to avoid packaging recomputes altering qty
    await record.update({
      product_packaging_id: false,
      product_packaging_qty: 0,
      product_uom: uomTuple,
      // product_uom_qty: qty,
    });
    await record.update({
      product_uom_qty: qty,
    });
  }

  // 3) set your per-pair price override last
  if (
    Object.prototype.hasOwnProperty.call(product, "price_unit_override") &&
    typeof product.price_unit_override === "number" &&
    !Number.isNaN(product.price_unit_override)
  ) {
    await record.update({ price_unit: product.price_unit_override });
  }
  // Write description last so it sticks
  if (product.line_description && (record.activeFields?.name || record.model?._config?.fields?.name)) {
    await record.update({ name: product.line_description });
  }
  
}

 
/* ---------- patch ---------- */

patch(SaleOrderLineProductField.prototype, {
  setup() {
    super.setup(...arguments);
    this.dialog = useService("dialog");
    this.notification = useService("notification");
    this.orm = useService("orm");
  },

  async _openProductConfigurator(edit = false) {
    const saleOrder = this.props.record.model.root;
    const partnerId = saleOrder.data.partner_id?.[0] || saleOrder.data.partner_id || saleOrder.data.order_partner_id?.[0];

    let ptavIds = (this.props.record.data.product_template_attribute_value_ids?.records || []).map(
      (r) => r.resId
    );

    let customAttributeValues = [];

    if (edit) {
      ptavIds = ptavIds.concat((this.props.record.data.product_no_variant_attribute_value_ids?.records || []).map(
          (r) => r.resId
      ));
      customAttributeValues = 
          this.props.record.data.product_custom_attribute_value_ids?.records?.[0]?.isNew ? 
          (this.props.record.data.product_custom_attribute_value_ids.records || []).map(
            (r) => r.data
          ) : 
          await this.orm.read(
            "product.attribute.custom.value",
            this.props.record.data.product_custom_attribute_value_ids?.currentIds || [],
            ["custom_product_template_attribute_value_id", "custom_value"]
          );
    }

    const tmplId = this.props.record.data.product_template_id?.[0];
    const [tmpl] = await this.orm.read("product.template", [tmplId], [
      "laterality_enabled",
      "laterality_default",
      "bilateral_default_type",
    ]);

    // Detect “editing an existing line” even if caller forgot to pass true
    const isExistingLine = !!this.props.record.data.id;
    const effectiveEdit = edit || isExistingLine;
    const mode    = this.props.record.data.laterality_mode || false;
    const payload = this.props.record.data.laterality_payload || {};
    const hasPayload = typeof mode === "string" && Object.keys(payload || {}).length > 0;
    const initLaterality = hasPayload ? { mode, payload } : { mode: "bilateral_shared", payload: {} };
    const confirmedUnitPrice = Number(this.props.record.data.price_unit || 0);
    
    // SAFE debug
    const il = initLaterality || {};
    console.log("[SOL → Dialog] initialLaterality", {
      mode: il.mode,
      hasPayload: !!(il.payload && Object.keys(il.payload).length),
      payloadKeys: Object.keys(il.payload || {}),
      payload: il.payload,
    });
    
    console.log("[SOL → Dialog] current SOL fields", {
      product_id: this.props.record.data.product_id,
      product_template_id: this.props.record.data.product_template_id,
      product_uom_qty: this.props.record.data.product_uom_qty,
    });

    const lateralityContext = {
      laterality_enabled: !!tmpl?.laterality_enabled,
      laterality_default: tmpl?.laterality_default || "bilateral",
      bilateral_default_type: tmpl?.bilateral_default_type || "shared",
    };

    const prefPayload = await this.orm.call(
      "product.template",
      "get_configurator_ptal_payload",
      [tmplId],
      { partner_id: partnerId } // kwargs
    );

    wrapUpdate(this.props.record, "MAIN_SOL");

    this.dialog.add(ProductConfiguratorDialog, {
      baseProductId: Number(this.props.record.data.product_id?.[0]) || undefined,
      productTemplateId: tmplId,
      ptavIds,
      ptalIdsWithPrefs: prefPayload.ptal_ids,
      customAttributeValues: customAttributeValues.map((d) => ({
        ptavId: d.custom_product_template_attribute_value_id[0],
        value: d.custom_value,
      })),
      confirmedUnitPrice,  
      initialLaterality: initLaterality,
      context: lateralityContext,
      partnerId,
      quantity: this.props.record.data.product_uom_qty,
      productUOMId: this.props.record.data.product_uom?.[0],
      companyId: saleOrder.data.company_id?.[0],
      pricelistId: saleOrder.data.pricelist_id?.[0],
      currencyId: this.props.record.data.currency_id?.[0],
      soDate: serializeDateTime(saleOrder.data.date_order),
      edit: effectiveEdit,
      save: async (mainProduct, optionalProducts, extraProducts) => {
        const isBilat = /^bilateral_/.test(mainProduct.laterality_mode || "");
        if (isBilat) {
          mainProduct.quantity = 1;
        }
        await this._onProductUpdate();
        const existingId = Number(this.props.record.data.product_id?.[0] || 0);
        const tuple = await ensureVariantTuple(this.orm, mainProduct, existingId);
        if (tuple) mainProduct.product_id = tuple;
      
        await applyProduct(this.props.record, mainProduct, "MAIN_SOL");
        
        saleOrder.data.order_line.leaveEditMode();
        
        for (const opt of optionalProducts) {
          const line = await saleOrder.data.order_line.addNewRecord({ position: "bottom", mode: "readonly" });
          await applyProduct(line, opt, "OPT_SOL");
        }
        for (const extra of extraProducts) {
          const line = await saleOrder.data.order_line.addNewRecord({ position: "bottom", mode: "readonly" });
          await applyProduct(line, extra, "EXTRA_SOL");
        }
      },
      discard: () => {
        saleOrder.data.order_line.delete(this.props.record);
      },
    });
  },

});
