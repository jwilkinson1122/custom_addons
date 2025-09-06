/** @odoo-module **/
import { ProductConfiguratorDialog } from "@sale_product_configurator/js/product_configurator_dialog/product_configurator_dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { serializeDateTime } from "@web/core/l10n/dates";
import { useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import {
  Component,
  onWillStart,
  useState,
  useSubEnv,
  useEffect,
} from "@odoo/owl";

patch(ProductConfiguratorDialog, {
  props: {
    ...ProductConfiguratorDialog.props,
    baseProductId: { type: Number, optional: true },
    context: { type: Object, optional: true },
    initialLaterality: { type: Object, optional: true },
  },
});

patch(ProductConfiguratorDialog.prototype, {
  setup() {
    super.setup();
    this.baseProductId = this.props.baseProductId || null;
    this._splitEpoch = 0;
    this._repriceDebounce = null;
    const ctx = this.props.context || {};
    this.lateralityEnabled = !!ctx.laterality_enabled;
    this.lateralityMode = ctx.laterality_default || "bilateral";
    this.bilateralType = ctx.bilateral_default_type || "shared";
    this.hybridGroups = new Set();
    this.sharedSelection = {};
    this.leftSelection = {};
    this.rightSelection = {};

    this.isGroupSplit = (groupKey) =>
      this.bilateralType === "split" || this.hybridGroups.has(groupKey);

    this.onToggleGroupSplit = (groupKey) => {
      if (this.hybridGroups.has(groupKey)) this.hybridGroups.delete(groupKey);
      else this.hybridGroups.add(groupKey);
      this.render(true);
    };

    this.afterToggleSanityCheck = () => {
      const isBilat = this.lateralityMode === "bilateral";
      const shouldShowPanel = isBilat && this.bilateralType === "split";
      const hasGroups = !!(this.attrGroups && this.attrGroups.length);
      console.log(
        "[sanity]",
        { isBilat, type: this.bilateralType, shouldShowPanel, hasGroups },
        "If shouldShowPanel && !hasGroups, your attrGroups builder returned []"
      );
    };

    this.onPickSideValue = (side, attrId, valueId) => {
      if (side === "left") this.leftSelection[attrId] = valueId;
      else if (side === "right") this.rightSelection[attrId] = valueId;
      else this.sharedSelection[attrId] = valueId;
      this.render(true);
    };

    this.state = useState({
      products: [],
      optionalProducts: [],
      extraProducts: [],
      quantityList: [],
      siNo: 0,
      qtyMode: false,
    });

    this.orm = useService("orm");
    this.rootRef = useRef("root");

    this.removeQuantity = this.removeQuantity.bind(this);
    this.handleTabOnLength = this.handleTabOnLength.bind(this);


    // Build a per-PTAV map once
    const prefByPtav = new Map();
    for (const line of this.props.ptalIdsWithPrefs || []) {
      for (const v of line.ptav_ids || []) {
        prefByPtav.set(Number(v.id), {
          left: !!v.isPreferredLeft,
          right: !!v.isPreferredRight,
          any: !!v.isPreferred,
          noteLeft: v.noteLeft || "",
          noteRight: v.noteRight || "",
        });
      }
    }

    useSubEnv({
      prefByPtav, 
      laterality: {
        enabled: this.lateralityEnabled,
        mode: () => this.lateralityMode,
        isGlobalSplit: () => this.bilateralType === "split",
      },
      lrUI: {
        groups: () => this.attrGroups || [],
        isGroupSplit: (key) =>
          this.bilateralType === "split" || this.hybridGroups.has(key),
        leftSel: () => this.leftSelection,
        rightSel: () => this.rightSelection,
        pick: async (side, attrId, pavOrPtavId) => {
          attrId = +attrId;
          pavOrPtavId = +pavOrPtavId;

          // keep your UI mirrors
          if (side === "left") this.leftSelection[attrId] = pavOrPtavId;
          if (side === "right") this.rightSelection[attrId] = pavOrPtavId;
          if (this.bilateralType !== "split")
            this.sharedSelection[attrId] = pavOrPtavId;

          const row =
            this.bilateralType === "split"
              ? this._findRowBySide(side)
              : this._findMainRow();
          if (!row) return;

          await this._ensurePtavIndex(row.product_tmpl_id);

          // PAV -> PTAV (or pass-through if already PTAV)
          let ptav = this._ptavFor(row, attrId, pavOrPtavId);
          if (!ptav) {
            ptav = await this._resolvePtavOnline(
              row.product_tmpl_id,
              attrId,
              pavOrPtavId
            );
            if (ptav) {
              this._ptavIndex[row.product_tmpl_id] ||= {};
              this._ptavIndex[row.product_tmpl_id][attrId] ||= {};
              this._ptavIndex[row.product_tmpl_id][attrId][pavOrPtavId] = ptav;
            }
          }
          if (!ptav) {
            console.warn(
              "[pick] could not resolve PTAV for attr",
              attrId,
              "pav/ptav",
              pavOrPtavId
            );
            return;
          }

          // ←— CRUCIAL: find the correct PTAL even if attrId didn't match locally
          const line = this._findLineForSelection(row, attrId, ptav);
          if (!line) {
            console.warn("[pick] no PTAL found for attr", attrId, "ptav", ptav);
            return;
          }

          // Multi-safe toggle (default to single if no flag)
          const multi = !!line.multi;
          let selected = (line.selected_attribute_value_ids || []).map(Number);
          if (multi) {
            selected = selected.includes(ptav)
              ? selected.filter((id) => id !== ptav)
              : [...selected, ptav];
          } else {
            selected = [ptav];
          }
          line.selected_attribute_value_ids = selected;

          console.log(
            "LINE AFTER SET",
            JSON.stringify({
              side,
              attrId,
              selected_after: line.selected_attribute_value_ids,
            })
          );

          // Safer: snapshot only what we need to avoid circular structures
          console.log(
            "ROW LINES SNAPSHOT",
            JSON.stringify(
              row.attribute_lines.map((l) => ({
                attr: Array.isArray(l.attribute_id)
                  ? l.attribute_id[0]
                  : l?.attribute_id?.id ?? l.attribute_id,
                selected: l.selected_attribute_value_ids,
              }))
            )
          );

          try {
            await this._reprice(row);
          } catch (e) {
            console.error("[pick] _reprice failed", e);
          } finally {
            this.render(true);
          }
        },

        toggleGlobal: this.onToggleSplit.bind(this),
        toggleGroup: (key) => {
          if (!key) return;
          if (this.hybridGroups.has(key)) this.hybridGroups.delete(key);
          else this.hybridGroups.add(key);
          this.render(true);
        },
      },
    });

    useEffect(
      () => {
        console.log(
          "LateralityEnabled:",
          this.lateralityEnabled,
          "Mode:",
          this.lateralityMode,
          "Type:",
          this.bilateralType,
          "Groups:",
          this.attrGroups
        );

        if (
          this.state.qtyMode &&
          this.state.quantityList.length > 0 &&
          this.rootRef.el
        ) {
          const inputs = this.rootRef.el.querySelectorAll(
            'input[name="extra_quantity"]'
          );
          inputs[inputs.length - 1]?.focus();
        }
      },
      () => [
        this.state.quantityList.length,
        this.state.qtyMode,
        this.lateralityEnabled,
        this.lateralityMode,
        this.bilateralType,
        (this.attrGroups || []).length, // guards undefined
      ]
    );

    onWillStart(async () => {
      await this._initData();
      const main = this._findMainRow();
      const partnerId = this.props.partnerId || this.props.context?.partner_id;
      if (main && partnerId) {
        const prefs = await this.orm.call(
          "product.template",
          "get_configurator_ptal_payload",
          [main.product_tmpl_id, partnerId]
        );
        this._applyPreferences(prefs); // (defined below)
      }
      if (this.props.initialLaterality) {
        console.log(
          "[Dialog.onWillStart] restoring laterality",
          this.props.initialLaterality
        );
        await this._restoreLaterality(this.props.initialLaterality);
        console.log("[Dialog.onWillStart] after _restoreLaterality", {
          mode: this.lateralityMode,
          type: this.bilateralType,
          left: this._findRowBySide("left"),
          right: this._findRowBySide("right"),
          main: this._findMainRow(),
        });
      }
    });
  },

  // --- Data Load/Init ---------------------------------------

  async _initData() {
    const { products, optional_products } = await this._loadData(
      this.props.edit
    );
    this.state.products = products;
    this._ptavIndex = {};
    const mainRow = this.state.products?.[0];
    if (mainRow) {
      const idx = (this._ptavIndex[mainRow.product_tmpl_id] = {});
      for (const ptal of mainRow.attribute_lines || []) {
        const attrId = Array.isArray(ptal.attribute_id)
          ? ptal.attribute_id[0]
          : ptal.attribute_id;
        const map = (idx[attrId] = {});
        for (const v of ptal.attribute_values || []) {
          const pavId = Array.isArray(v.product_attribute_value_id)
            ? v.product_attribute_value_id[0]
            : v.product_attribute_value_id ?? v.pav_id ?? v.value_id ?? null;
          if (pavId) map[Number(pavId)] = Number(v.id); // PAV -> PTAV
        }
      }
    }

    this.state.optionalProducts = optional_products;
    const main = this.state.products?.[0];
    this.attrGroups = [];
    this.attrIdToGroupKey = {};

    // helper to extract an id safely
    const getId = (a) => {
      if (Array.isArray(a)) return a[0];
      if (a && typeof a === "object" && "id" in a) return a.id;
      if (typeof a === "number") return a;
      return null;
    };

    // 1) Try client payload first
    let attributeLines = Array.isArray(main?.attribute_lines)
      ? main.attribute_lines
      : [];

    // 2) If empty or missing IDs, read from the server (PTAL)
    if (
      !attributeLines.length ||
      !attributeLines.some((l) => getId(l.attribute_id))
    ) {
      if (main?.product_tmpl_id) {
        const ptalRows = await this.orm.searchRead(
          "product.template.attribute.line",
          [["product_tmpl_id", "=", main.product_tmpl_id]],
          ["attribute_id", "value_ids"]
        );
        // enrich PTAL rows with names & values
        const attrIds = ptalRows
          .map((r) => getId(r.attribute_id))
          .filter(Boolean);
        const valIds = [...new Set(ptalRows.flatMap((r) => r.value_ids || []))];
        const [attrRows, ptavRows] = await Promise.all([
          this.orm.searchRead(
            "product.attribute",
            [["id", "in", attrIds]],
            ["name", "attribute_group_id", "sequence_group"]
          ),
          valIds.length
            ? this.orm.searchRead(
                "product.template.attribute.value",
                [["id", "in", valIds]],
                // grab a few useful fields; name is fine for the UI
                [
                  "name",
                  "attribute_id",
                  "price_extra",
                  "attribute_line_id",
                  "product_tmpl_id",
                  "product_attribute_value_id",
                ]
              )
            : Promise.resolve([]),
        ]);

        const attrById = Object.fromEntries(attrRows.map((a) => [a.id, a]));
        const valsById = Object.fromEntries(ptavRows.map((v) => [v.id, v]));

        attributeLines = ptalRows.map((r) => {
          const aid = getId(r.attribute_id);
          return {
            attribute_id: aid,
            attribute_name:
              attrById[aid]?.name ||
              (Array.isArray(r.attribute_id)
                ? r.attribute_id[1]
                : `Attribute ${aid}`),
            // IMPORTANT: r.value_ids are PTAV ids; keep them as-is
            attribute_values: (r.value_ids || []).map((id) => {
              const v = valsById[id] || {};
              return { id, name: v.name || `Value ${id}` }; // `id` is PTAV id
            }),
          };
        });
      }
    }

    // 3) Group by your new product.attribute.group fields
    if (attributeLines.length) {
      const attrIds = attributeLines
        .map((l) => getId(l.attribute_id))
        .filter(Boolean);
      const attrMeta = await this.orm.searchRead(
        "product.attribute",
        [["id", "in", attrIds]],
        ["name", "attribute_group_id", "sequence_group"]
      );
      const byId = Object.fromEntries(attrMeta.map((a) => [a.id, a]));
      const getKey = (a) =>
        (a.attribute_group_id && a.attribute_group_id[0]) || "nogroup";
      const getName = (a) =>
        (a.attribute_group_id && a.attribute_group_id[1]) || "Other";
      const getSeq = (a) =>
        typeof a.sequence_group === "number" ? a.sequence_group : 999;

      const groups = new Map();
      for (const line of attributeLines) {
        const aid = getId(line.attribute_id);
        const a = byId[aid];
        if (!aid || !a) continue;

        const key = getKey(a);
        if (!groups.has(key)) {
          groups.set(key, { key, name: getName(a), seq: getSeq(a), attrs: [] });
        }
        groups.get(key).attrs.push({
          ...line,
          attribute_id: aid,
          attribute_name: line.attribute_name || a.name || `Attribute ${aid}`,
          attribute_values: line.attribute_values || [],
        });
        this.attrIdToGroupKey[aid] = key;
      }

      this.attrGroups = [...groups.values()].sort(
        (x, y) => x.seq - y.seq || x.name.localeCompare(y.name)
      );
    }

    // (keep your existing custom value setup & qty mode)
    for (const customValue of this.props.customAttributeValues) {
      this._updatePTAVCustomValue(
        this.env.mainProductTmplId,
        customValue.ptavId,
        customValue.value
      );
    }
    this._checkExclusions(this.state.products[0]);

    if (this.state.products.length > 0) {
      const tmplId = this.state.products[0].product_tmpl_id;
      const rows = await this.orm.searchRead(
        "product.template",
        [["id", "=", tmplId]],
        ["allow_qty_mode"]
      );
      if (rows && rows[0]) {
        this.state.qtyMode = !!rows[0].allow_qty_mode;
      }
    }

    this.render(true);
  },

  async _ensurePtavIndex(tmplId) {
    this._ptavIndex ||= {};
    if (
      this._ptavIndex[tmplId] &&
      Object.keys(this._ptavIndex[tmplId]).length
    ) {
      return; // already built
    }
    const ptalRows = await this.orm.searchRead(
      "product.template.attribute.line",
      [["product_tmpl_id", "=", tmplId]],
      ["attribute_id", "value_ids"]
    );
    const attrIds = ptalRows.map((r) =>
      Array.isArray(r.attribute_id) ? r.attribute_id[0] : r.attribute_id
    );
    const ptavIds = [...new Set(ptalRows.flatMap((r) => r.value_ids || []))];

    const ptavRows = ptavIds.length
      ? await this.orm.searchRead(
          "product.template.attribute.value",
          [["id", "in", ptavIds]],
          ["id", "attribute_id", "product_attribute_value_id"] // <- gives us PAV id
        )
      : [];

    // Build: index[attrId][pavId] = ptavId
    const idx = {};
    for (const r of ptavRows) {
      const aid = Array.isArray(r.attribute_id)
        ? r.attribute_id[0]
        : r.attribute_id;
      const pav = Array.isArray(r.product_attribute_value_id)
        ? r.product_attribute_value_id[0]
        : r.product_attribute_value_id;
      if (aid && pav) {
        idx[aid] ||= {};
        idx[aid][Number(pav)] = Number(r.id);
      }
    }
    this._ptavIndex[tmplId] = idx;
  },

  async _resolvePtavOnline(tmplId, attrId, pavId) {
    const rows = await this.orm.searchRead(
      "product.template.attribute.value",
      [
        ["product_tmpl_id", "=", tmplId],
        ["product_attribute_value_id", "=", pavId],
        ["attribute_id", "=", attrId],
      ],
      ["id"]
    );
    return rows?.[0]?.id ? Number(rows[0].id) : null;
  },

  _getLineAttrId(line) {
    const a = line?.attribute_id ?? line?.attribute;
    return Array.isArray(a) ? a[0] : a?.id ?? a;
  },

  _findLineForSelection(row, attrId, ptav) {
    let line = row.attribute_lines.find(
      (l) => Number(this._getLineAttrId(l)) === Number(attrId)
    );
    if (line) return line;
    line = row.attribute_lines.find((l) =>
      (l.attribute_values || []).some(
        (v) => Number(v?.id ?? v) === Number(ptav)
      )
    );
    return line || null;
  },

  async _reprice(product) {
    const comb = (product.attribute_lines || []).flatMap(
      (l) => l.selected_attribute_value_ids || []
    );
    console.log(
      "[repricing] side=",
      product._side || "shared",
      "qty=",
      product.quantity,
      "PTAVs=",
      comb
    );
    if (!product) return;
    try {
      console.log(
        "[repricing] PTAVs=",
        (product.attribute_lines || []).flatMap(
          (l) => l.selected_attribute_value_ids
        )
      );
      const updated = await this._updateCombination(
        product,
        Number(product.quantity || 1)
      );
      Object.assign(product, updated);
      product._variant_id =
        (Array.isArray(updated.product_id)
          ? updated.product_id[0]
          : updated.product_id) ||
        (Array.isArray(updated.product_product_id)
          ? updated.product_product_id[0]
          : updated.product_product_id) ||
        product._variant_id ||
        null;
      delete product._combined_price;
      const left = this._findRowBySide("left");
      const right = this._findRowBySide("right");
      if (left) delete left._combined_price;
      if (right) delete right._combined_price;
      const main = this._findMainRow();
      if (main && this.bilateralType !== "split") delete main._combined_price;
      // if (main && !this.bilateralType === 'split') delete main._combined_price;
      // Keep twin prices in sync for Bilateral Split
      if (this.bilateralType === "split") {
        const left = this._findRowBySide("left");
        const right = this._findRowBySide("right");
        if (left && right) {
          left._twin_price = Number(right.price || 0);
          right._twin_price = Number(left.price || 0);
        }
      } else {
        const main = this._findMainRow();
        if (main) delete main._twin_price;
      }
      this._checkExclusions(product);
      this._updateSplitHeaderSummary(product);
    } catch (err) {
      console.log("[repricing] failed", err);
    } finally {
      // Always force a paint even if the RPC errored
      this.render(true);
    }
  },

  _updateSplitHeaderSummary(product) {
    // Only in global split, on the main template rows
    if (
      !(
        this.lateralityMode === "bilateral" &&
        this.bilateralType === "split" &&
        product.product_tmpl_id === this.env.mainProductTmplId
      )
    ) {
      return;
    }
    // If we're updating the left row, store the right price on it
    if (product._side === "left") {
      const right = this._findRowBySide("right");
      const r = right ? Number(right.price ?? right.list_price ?? 0) : 0;
      product._twin_price = r; // this is used by the template
    }
    // If we updated the right row, mirror its price onto the left, too
    if (product._side === "right") {
      const left = this._findRowBySide("left") || this._findMainRow();
      if (left) {
        const r = Number(product.price ?? product.list_price ?? 0);
        left._twin_price = r;
      }
    }
  },

  _ptavFor(row, attrId, maybePavOrPtav) {
    const id = Number(maybePavOrPtav);
    // If the id is already present among the PTAVs on the line, accept it.
    const getAttrId = (a) => (Array.isArray(a) ? a[0] : a?.id ?? a);
    const line = row.attribute_lines.find(
      (l) => Number(getAttrId(l.attribute_id)) === Number(attrId)
    );
    if (!line) return null;

    if (line.attribute_values?.some((v) => Number(v.id) === id)) {
      return id; // already PTAV
    }
    // Otherwise, try to resolve from PAV -> PTAV.
    const tmplId = row.product_tmpl_id;
    return this._ptavIndex?.[tmplId]?.[Number(attrId)]?.[id] ?? null;
  },

  _findMainRow() {
    const byId = this.state.products.find(
      (p) => p.product_tmpl_id === this.env.mainProductTmplId
    );
    return byId || this.state.products[0] || null;
  },

  _findRowBySide(side) {
    return this.state.products.find(
      (p) =>
        p.product_tmpl_id === this.env.mainProductTmplId &&
        (p._side === side || (!p._side && side === "left"))
    );
  },

  _mirrorToMainPTAL(attrId, ptavId) {
    if (this.bilateralType === "split") return;
    const main = this.state.products.find(
      (p) => p.product_tmpl_id === this.env.mainProductTmplId
    );
    if (!main) return;
    const getAttrId = (a) => (Array.isArray(a) ? a[0] : a?.id ?? a);
    const line = main.attribute_lines.find(
      (l) => Number(getAttrId(l.attribute_id)) === Number(attrId)
    );
    if (!line) return;
    line.selected_attribute_value_ids = [Number(ptavId)]; // PTAV here
    this._checkExclusions(main);
    return main;
  },

  _mirrorToSidePTAL(side, attrId, ptavId) {
    const row = this.state.products.find(
      (p) =>
        p.product_tmpl_id === this.env.mainProductTmplId &&
        (p._side === side || (!p._side && side === "left"))
    );
    if (!row) return;
    const getAttrId = (a) => (Array.isArray(a) ? a[0] : a?.id ?? a);
    const line = row.attribute_lines.find(
      (l) => Number(getAttrId(l.attribute_id)) === Number(attrId)
    );
    if (!line) return;
    line.selected_attribute_value_ids = [Number(ptavId)]; // PTAV here
    this._checkExclusions(row);
    return row;
  },

  _computeLateralityMode() {
    if (this.lateralityMode === "left_only") return "left_only";
    if (this.lateralityMode === "right_only") return "right_only";
    if (this.bilateralType === "split") return "bilateral_split";
    if (this.hybridGroups && this.hybridGroups.size) return "bilateral_hybrid"; // ✅
    return "bilateral_shared";
  },

  onToggleSplit(force = undefined) {
    // decide destination
    const goingToSplit =
      force === undefined ? this.bilateralType !== "split" : !!force;

    // set the flag first, don’t “flip” it
    this.bilateralType = goingToSplit ? "split" : "shared";

    const mainIdx = this.state.products.findIndex(
      (p) => p.product_tmpl_id === this.env.mainProductTmplId
    );
    if (mainIdx < 0) {
      this.render(true);
      return;
    }

    const getAttrId = (a) => (Array.isArray(a) ? a[0] : a?.id ?? a);
    const products = [...this.state.products];

    if (goingToSplit) {
      // ----- ensure we have left/right rows -----
      const hasRight = products.some(
        (p, i) =>
          i !== mainIdx &&
          p.product_tmpl_id === this.env.mainProductTmplId &&
          p._side === "right"
      );
      // start from a clean “main-as-left”
      const left = { ...products[mainIdx] };

      // seed selections as PTAV ids if empty
      if (!Object.keys(this.leftSelection).length) {
        for (const line of left.attribute_lines || []) {
          const aid = Number(getAttrId(line.attribute_id));
          const selPTAV = Number(
            (line.selected_attribute_value_ids || [0])[0] || 0
          );
          if (aid && selPTAV) this.leftSelection[aid] = selPTAV;
        }
      }
      // mirror to right (will get overwritten later by payload restore anyway)
      this.rightSelection = { ...this.leftSelection };

      // clone for right
      const right = JSON.parse(JSON.stringify(left));
      left._side = "left";
      right._side = "right";
      left.quantity = 1;
      right.quantity = 1;

      // label
      const baseName =
        products[mainIdx].display_name || products[mainIdx].name || "";
      left._base_display_name = baseName;
      right._base_display_name = baseName;
      left.display_name = `${baseName} — Left`;
      right.display_name = `${baseName} — Right`;

      // write current selections
      for (const line of left.attribute_lines || []) {
        const aid = Number(getAttrId(line.attribute_id));
        const sel = this.leftSelection[aid];
        line.selected_attribute_value_ids = sel ? [Number(sel)] : [];
      }
      for (const line of right.attribute_lines || []) {
        const aid = Number(getAttrId(line.attribute_id));
        const sel = this.rightSelection[aid];
        line.selected_attribute_value_ids = sel ? [Number(sel)] : [];
      }

      // replace main with left and (re)insert right
      products[mainIdx] = left;
      if (!hasRight) {
        products.splice(mainIdx + 1, 0, right);
      } else {
        // if a right exists but we couldn’t find it (edge case), we still ensure
        // there’s one right next to left
        const existingRightIdx = products.findIndex(
          (p, i) =>
            i !== mainIdx &&
            p.product_tmpl_id === this.env.mainProductTmplId &&
            p._side === "right"
        );
        if (existingRightIdx < 0) {
          products.splice(mainIdx + 1, 0, right);
        }
      }
    } else {
      // ----- merge back to shared (unchanged from your current logic) -----
      const left = { ...products[mainIdx] };
      const rightIdx = products.findIndex(
        (p, i) =>
          i !== mainIdx &&
          p.product_tmpl_id === this.env.mainProductTmplId &&
          p._side === "right"
      );
      if (rightIdx >= 0) products.splice(rightIdx, 1);

      left._side = undefined;
      left.quantity = 2;

      const baseName =
        left._base_display_name ||
        left.display_name?.replace(/ — (Left|Right)$/, "") ||
        left.name ||
        "";
      left.display_name = baseName;
      delete left._base_display_name;

      const sharedFromLeft = {};
      for (const line of left.attribute_lines || []) {
        const aid = Number(getAttrId(line.attribute_id));
        const selPTAV = Number(
          (line.selected_attribute_value_ids || [0])[0] || 0
        );
        if (aid && selPTAV) sharedFromLeft[aid] = selPTAV;
      }
      this.sharedSelection = sharedFromLeft;
      for (const line of left.attribute_lines || []) {
        const aid = Number(getAttrId(line.attribute_id));
        const sel = this.sharedSelection[aid];
        line.selected_attribute_value_ids = sel ? [Number(sel)] : [];
      }

      products[mainIdx] = left;
    }

    this.state.products = products;
    this._splitEpoch = (this._splitEpoch || 0) + 1;
    this.render(true);

    Promise.resolve().then(async () => {
      const leftRow =
        this.state.products.find(
          (p) =>
            p.product_tmpl_id === this.env.mainProductTmplId &&
            p._side === "left"
        ) ||
        this.state.products.find(
          (p) => p.product_tmpl_id === this.env.mainProductTmplId
        );
      const rightRow = this.state.products.find(
        (p) =>
          p.product_tmpl_id === this.env.mainProductTmplId &&
          p._side === "right"
      );
      if (leftRow) await this._reprice(leftRow);
      if (rightRow) await this._reprice(rightRow);
    });
  },

  onToggleHybrid(groupXmlId) {
    if (this.hybridGroups.has(groupXmlId)) this.hybridGroups.delete(groupXmlId);
    else this.hybridGroups.add(groupXmlId);
    this.render(true);
  },

  async onLateralityChange(mode) {
    // Update top-level mode flag
    this.lateralityMode = mode;

    // Locate the main row once
    const mainIdx = this.state.products.findIndex(
      (p) => p.product_tmpl_id === this.env.mainProductTmplId
    );
    if (mainIdx < 0) {
      this.render(true);
      return;
    }
    const main = this.state.products[mainIdx];

    // ---- Non-bilateral: collapse to a single row (shared) ----
    if (mode !== "bilateral") {
      this.bilateralType = "shared";

      // Identify side rows if we were split; choose source for unified selection
      const leftRow = this._findRowBySide("left") || main;
      const rightRow = this._findRowBySide("right");
      const srcRow = mode === "right_only" ? rightRow || leftRow : leftRow;

      // Drop right row if present
      const rightIdx = this.state.products.findIndex(
        (p, i) =>
          i !== mainIdx &&
          p.product_tmpl_id === this.env.mainProductTmplId &&
          p._side === "right"
      );
      if (rightIdx >= 0) this.state.products.splice(rightIdx, 1);

      // Normalize the main row
      main._side = undefined;
      delete main._twin_price;
      main.quantity = 1;

      // Restore base display name (strip “ — Left/Right” if set)
      const baseName =
        main._base_display_name ||
        (main.display_name
          ? main.display_name.replace(/ — (Left|Right)$/, "")
          : "") ||
        main.name ||
        "";
      main.display_name = baseName;
      delete main._base_display_name;

      // Copy the chosen side's PTAV selection into the unified main row
      this.sharedSelection = {}; // keep client mirrors consistent
      for (const line of main.attribute_lines || []) {
        const aid = Number(this._getLineAttrId(line));
        const srcLine = (srcRow?.attribute_lines || []).find(
          (l) => Number(this._getLineAttrId(l)) === aid
        );
        const selPTAV = Number(
          (srcLine?.selected_attribute_value_ids || [])[0] || 0
        );
        line.selected_attribute_value_ids = selPTAV ? [selPTAV] : [];
        if (aid && selPTAV) this.sharedSelection[aid] = selPTAV;
      }

      // Selections are unified; side mirrors no longer apply
      this.leftSelection = {};
      this.rightSelection = {};

      this._checkExclusions(main);
      await this._reprice(main);
      this.render(true);
      return;
    }

    // ---- Bilateral branch: keep two sides (shared/split handled elsewhere) ----
    // If you want the configurator to visually show “×2”, uncomment below:
    const q = Number(main.quantity || 0);
    main.quantity = q >= 2 ? (q % 2 === 0 ? q : q + 1) : 2;

    this._checkExclusions(main);
    this.render(true);
  },

  async _restoreLaterality(initial) {
    const inObj = initial || {};
    // Guard/coerce the incoming shape
    const mode =
      typeof inObj.mode === "string" && inObj.mode
        ? inObj.mode
        : "bilateral_shared";
    const payload =
      inObj && typeof inObj.payload === "object" && inObj.payload
        ? inObj.payload
        : {};

    // Normalize flags
    this.lateralityMode = mode.startsWith("bilateral") ? "bilateral" : mode;
    this.bilateralType = mode === "bilateral_split" ? "split" : "shared";
    this.hybridGroups = new Set(payload.hybrid_groups || []);

    const main = this._findMainRow();
    if (!main) {
      console.warn("[Dialog] No main row yet, aborting laterality restore");
      return;
    }
    await this._ensurePtavIndex(main.product_tmpl_id);

    const normalizeSel = (sel = {}) =>
      Object.fromEntries(
        Object.entries(sel).map(([k, v]) => [Number(k), Number(v)])
      );

    const writeSelectionIntoRow = async (
      row,
      selection = {},
      side = "shared"
    ) => {
      if (!row || !Array.isArray(row.attribute_lines)) {
        console.warn("[Dialog] writeSelectionIntoRow skipped", {
          side,
          hasRow: !!row,
        });
        return;
      }
      const tmplId = row.product_tmpl_id;
      for (const [attrIdStr, pavOrPtav] of Object.entries(selection)) {
        const attrId = Number(attrIdStr);
        const line = row.attribute_lines.find(
          (l) => Number(this._getLineAttrId(l)) === attrId
        );
        if (!line) {
          console.warn("[Dialog] PTAL not found", { side, attrId });
          continue;
        }
        // Accept PTAV directly or resolve PAV -> PTAV
        let ptav = Number(pavOrPtav);
        const onLine = (line.attribute_values || []).some(
          (v) => Number(v?.id ?? v) === ptav
        );
        if (!onLine) {
          ptav =
            this._ptavIndex?.[tmplId]?.[attrId]?.[Number(pavOrPtav)] ??
            (await this._resolvePtavOnline(tmplId, attrId, Number(pavOrPtav)));
          if (ptav) {
            this._ptavIndex[tmplId] ||= {};
            this._ptavIndex[tmplId][attrId] ||= {};
            this._ptavIndex[tmplId][attrId][Number(pavOrPtav)] = ptav;
          }
        }
        line.selected_attribute_value_ids = ptav ? [ptav] : [];
      }
    };

    if (this.bilateralType === "split") {
      // Scaffold right row if needed
      if (!this._findRowBySide("right")) {
        this.onToggleSplit(true);
        await Promise.resolve(); // let state settle
      }

      const leftRow = this._findRowBySide("left") || this._findMainRow();
      const rightRow = this._findRowBySide("right");

      const leftSel = normalizeSel(payload.left);
      const rightSel = normalizeSel(payload.right);

      await writeSelectionIntoRow(leftRow, leftSel, "left");
      await writeSelectionIntoRow(rightRow, rightSel, "right");

      this.leftSelection = { ...leftSel };
      this.rightSelection = { ...rightSel };

      if (leftRow) leftRow.quantity = 1;
      if (rightRow) rightRow.quantity = 1;
    } else {
      // Merge back to shared if currently split
      if (this._findRowBySide("right")) {
        this.onToggleSplit(false);
        await Promise.resolve();
      }

      const unified = this._findMainRow();
      const sharedSel = normalizeSel(payload.shared);

      await writeSelectionIntoRow(unified, sharedSel, "shared");
      this.sharedSelection = { ...sharedSel };

      // Keep even qty ≥ 2 so UI renders “unit × qty”
      if (this.lateralityMode === "bilateral" && unified) {
        const q = Number(unified.quantity || 0);
        unified.quantity = q >= 2 ? (q % 2 === 0 ? q : q + 1) : 2;
        delete unified._combined_price; // ensure we show unit × qty, not a cached total
      }
    }

    // Reprice
    const L = this._findRowBySide("left");
    const R = this._findRowBySide("right");
    if (L) await this._reprice(L);
    if (R) await this._reprice(R);

    // Only show combined total in split
    if (this.bilateralType === "split" && L && R) {
      const n = (v) => Number(v ?? 0);
      const recomputed =
        n(L.price ?? L.list_price) + n(R.price ?? R.list_price);
      const confirmed = Number(this.props.confirmedUnitPrice || 0);
      const combined = confirmed > 0 ? confirmed : recomputed;
      L._combined_price = combined;
      R._combined_price = combined;
    }

    console.log("[Dialog] _restoreLaterality done", {
      lateralityMode: this.lateralityMode,
      bilateralType: this.bilateralType,
    });

    const computedMode = this._computeLateralityMode?.();
    console.warn("[Dialog] mode check", { mode, computedMode });

    this.render(true);
  },

  onPickShared(attrId, valueId) {
    this.sharedSelection[attrId] = valueId;
  },
  onPickLeft(attrId, valueId) {
    this.leftSelection[attrId] = valueId;
  },
  onPickRight(attrId, valueId) {
    this.rightSelection[attrId] = valueId;
  },

  // ---------- Qty mode UI handlers ----------

  onButtonClick() {
    this.state.siNo += 1;
    this.state.quantityList.push({
      id: this.state.siNo,
      quantity: "",
      siNo: this.state.siNo,
      length: "",
    });
    this.render();
  },

  removeQuantity(quantityId) {
    const updated = this.state.quantityList.filter(
      (item) => item.id !== quantityId
    );
    updated.forEach((item, idx) => {
      item.siNo = idx + 1;
    });
    this.state.quantityList = updated;
    this.state.siNo = updated.length;
    this.render();
  },

  handleTabOnLength(ev, quantity) {
    if (ev.key === "Tab") {
      const last = this.state.quantityList[this.state.quantityList.length - 1];
      if (last && quantity.id === last.id) this.onButtonClick();
    }
  },

  async findPairUoMId(orm, currentUomId) {
    if (!currentUomId) return null;
    const [u] = await orm.read("uom.uom", [currentUomId], ["category_id"]);
    if (!u?.category_id) return null;
    const rows = await orm.searchRead(
      "uom.uom",
      [
        ["category_id", "=", u.category_id[0]],
        ["uom_type", "=", "bigger"],
        ["factor_inv", "=", 2],
      ],
      ["id"]
    );
    return rows?.[0]?.id || null;
  },

  async findPairUoM(orm, baseUomId) {
    if (!baseUomId) return null;
    const [base] = await orm.read("uom.uom", [baseUomId], ["category_id"]);
    const catId = base?.category_id?.[0];
    if (!catId) return null;
    const rows = await orm.searchRead(
      "uom.uom",
      [
        ["category_id", "=", catId],
        ["uom_type", "=", "bigger"],
        ["factor_inv", "=", 2],
      ],
      ["id", "name"]
    );
    return rows?.[0] ? { id: rows[0].id, name: rows[0].name } : null;
  },

  _attrDisplayName(line) {
    return (
      line.attribute_name ||
      (Array.isArray(line.attribute_id)
        ? line.attribute_id[1]
        : line?.attribute?.name || "Attribute")
    );
  },

  // _selectedPairs(row) {
  //     const out = [];
  //     for (const line of row?.attribute_lines || []) {
  //         const selId = Number((line.selected_attribute_value_ids || [])[0] || 0);
  //         if (!selId) continue;
  //         const val = (line.attribute_values || []).find(v => Number(v.id) === selId);
  //         out.push([this._attrDisplayName(line), val?.name || `#${selId}`]);
  //     }
  //     return out;
  // },

  _selectedPairs(row) {
    const out = [];
    for (const line of row?.attribute_lines || []) {
      const selId = Number((line.selected_attribute_value_ids || [])[0] || 0);
      if (!selId) continue;
      const val = (line.attribute_values || []).find(
        (v) => Number(v.id) === selId
      );
      const star = val?.isPreferred ? " ★" : "";
      out.push([
        this._attrDisplayName(line),
        (val?.name || `#${selId}`) + star,
      ]);
    }
    return out;
  },

  _formatSideBlock(sideLabel, row, { bullets = false } = {}) {
    const pairs = this._selectedPairs(row);
    if (!pairs.length) return null;

    if (bullets) {
      const lines = pairs.map(([a, v]) => `• ${a}: ${v}`).join("\n");
      return `${sideLabel}\n${lines}`;
    }
    const joined = pairs.map(([a, v]) => `${a}: ${v}`).join("; ");
    return `${sideLabel} — ${joined}`;
  },

  _scopeFor(line, dialog) {
    // If bilateral split, use left/right depending on which row the line belongs to
    if (
      dialog.lateralityMode === "bilateral" &&
      dialog.bilateralType === "split"
    ) {
      if (dialog._rowSide?.get(line) === "left") return "left";
      if (dialog._rowSide?.get(line) === "right") return "right";
      return "shared";
    }
    if (dialog.lateralityMode === "left") return "left";
    if (dialog.lateralityMode === "right") return "right";
    return "shared";
  },

  async togglePreferred(line, value, desired) {
    try {
      const partnerId = this.props.partnerId || this.props.context?.partner_id;
      if (!partnerId) return;
      const payload = {
        partner_id: partnerId,
        product_tmpl_id: this._findMainRow()?.product_tmpl_id,
        attribute_id: Number(line.attribute_id),
        pav_id: Number(
          value.product_attribute_value_id ||
            value.pav_id ||
            value.pavId ||
            value.pav ||
            value.id
        ), // be liberal
        scope: this._scopeFor(line, this),
        preferred: !!desired,
      };
      // model + method from Python above
      await this.orm.call(
        "product.config.preference",
        "toggle_preference",
        [],
        payload
      );

      // optimistic UI: flag the value
      // value.isPreferred = !!desired;
      // if (payload.scope === "left") value.isPreferredLeft = !!desired;
      // if (payload.scope === "right") value.isPreferredRight = !!desired;
      // if (payload.scope === "shared") {
      //   value.isPreferredLeft = value.isPreferredRight = !!desired;
      // }
      const m = this.env.prefByPtav;
      if (m && m.has(value.id)) {
        const entry = { ...m.get(value.id) };
        if (scope === "left")  entry.left  = !!desired;
        if (scope === "right") entry.right = !!desired;
        if (scope === "shared") entry.left = entry.right = entry.any = !!desired;
        m.set(value.id, entry);
      }
      this.render(true);
    } catch (e) {
      this.notification.add("Could not update preference.", { type: "danger" });
      throw e;
    }
  },

  _applyPreferences(prefs) {
    if (!prefs) return;
    const pick = (line, ptavId) => {
      if (!ptavId) return;
      // only preselect if nothing chosen yet on that line
      const sel = line.selected_attribute_value_ids || [];
      if (!sel.length) line.selected_attribute_value_ids = [Number(ptavId)];
    };

    // annotate values for UI badges, and remember notes
    const notes = prefs.notes || {};
    const preferredPtavIds = new Set(
      [
        ...Object.values(prefs.shared || {}),
        ...Object.values(prefs.left || {}),
        ...Object.values(prefs.right || {}),
      ].map(Number)
    );

    for (const group of this.attrGroups || []) {
      for (const line of group.attrs || []) {
        const aid = Number(line.attribute_id);
        (line.attribute_values || []).forEach((v) => {
          const isPreferred =
            preferredPtavIds.has(Number(v.id)) ||
            prefs.shared?.[aid] === v.id ||
            prefs.left?.[aid] === v.id ||
            prefs.right?.[aid] === v.id;
          v.isPreferred = !!isPreferred;
          if (notes[v.id]) v.note = notes[v.id];
        });
        // preselect (shared): only when dialog opens with no prior picks
        if (!line.selected_attribute_value_ids?.length) {
          if (prefs.shared?.[aid]) pick(line, prefs.shared[aid]);
        }
      }
    }

    // Per-side initialization: if you’re in split laterality OR you see per-side prefs,
    // seed left/right mirrors and flip the affected groups to split automatically.
    const hasSidePrefs =
      Object.keys(prefs.left || {}).length ||
      Object.keys(prefs.right || {}).length;

    if (
      this.lateralityMode === "bilateral" &&
      (this.bilateralType === "split" || hasSidePrefs)
    ) {
      // ensure split rows exist
      if (this.bilateralType !== "split") this.onToggleSplit(true);

      const left = this._findRowBySide("left");
      const right = this._findRowBySide("right");
      const byAid = (row) =>
        Object.fromEntries(
          (row?.attribute_lines || []).map((l) => [
            Number(this._getLineAttrId(l)),
            l,
          ])
        );

      const L = byAid(left),
        R = byAid(right);

      for (const [aidStr, ptavId] of Object.entries(prefs.left || {})) {
        const aid = Number(aidStr);
        if (L[aid] && !L[aid].selected_attribute_value_ids?.length) {
          L[aid].selected_attribute_value_ids = [Number(ptavId)];
        }
      }
      for (const [aidStr, ptavId] of Object.entries(prefs.right || {})) {
        const aid = Number(aidStr);
        if (R[aid] && !R[aid].selected_attribute_value_ids?.length) {
          R[aid].selected_attribute_value_ids = [Number(ptavId)];
        }
      }

      // If a given attribute’s left/right picks differ, mark its group as split (hybrid)
      const diffAids = new Set();
      for (const [aidStr, lId] of Object.entries(prefs.left || {})) {
        const aid = Number(aidStr);
        const rId = Number(prefs.right?.[aid] || 0);
        if (rId && Number(lId) !== rId) {
          const gKey = this.attrIdToGroupKey?.[aid];
          if (gKey) this.hybridGroups.add(gKey);
          diffAids.add(aid);
        }
      }

      // seed state mirrors (so your UI summary/name builder shows them immediately)
      this.leftSelection ||= {};
      this.rightSelection ||= {};
      Object.entries(prefs.left || {}).forEach(
        ([aid, ptav]) => (this.leftSelection[Number(aid)] = Number(ptav))
      );
      Object.entries(prefs.right || {}).forEach(
        ([aid, ptav]) => (this.rightSelection[Number(aid)] = Number(ptav))
      );
    }

    this.render(true);
  },

  _buildSOLName({ mode, main, leftRow, rightRow, bullets = false }) {
    const base =
      main._base_display_name || main.display_name || main.name || "";
    const lines = [base];

    if (mode === "bilateral_split") {
      const L = this._formatSideBlock("Left", leftRow || main, { bullets });
      const R = this._formatSideBlock("Right", rightRow || main, { bullets });
      if (L) lines.push(L);
      if (R) lines.push(R);
    } else if (mode === "bilateral_shared" || mode === "bilateral_hybrid") {
      const P = this._formatSideBlock("Bilateral", main, { bullets });
      // const P = this._formatSideBlock("Left & Right", main, { bullets });
      if (P) lines.push(P);
    } else {
      const label = mode === "left_only" ? "Left" : "Right";
      const S = this._formatSideBlock(label, main, { bullets });
      if (S) lines.push(S);
    }
    return lines.join("\n");
  },
  
  // ---------- Confirm flow ----------
  async onConfirm() {
    if (!this.isPossibleConfiguration()) return;

    const main = this.state.products.find(
      (p) => p.product_tmpl_id === this.env.mainProductTmplId
    );
    if (!main) return;

    // 1) Laterality: mode + payload
    const mode = this._computeLateralityMode();
    const isSplit = mode === "bilateral_split";
    const isBilateral =
      isSplit || mode === "bilateral_shared" || mode === "bilateral_hybrid";

    main.laterality_mode = mode;
    main.laterality_payload = {
      shared: this.sharedSelection,
      left: this.leftSelection,
      right: this.rightSelection,
      hybrid_groups: Array.from(this.hybridGroups),
      bilateral_type: this.bilateralType,
    };

    // 2) UoM & qty: Pair(s) + 1 pair for all bilateral
    if (isBilateral) {
      main.product_uom_qty = 1; // 1 pair
      try {
        const pair = await this.findPairUoM(this.orm, this.props.productUOMId);
        if (pair) main.product_uom = [pair.id, pair.name];
      } catch {
        /* non-fatal */
      }
    }

    // 3) Per-pair price override
    const n = (v) => Number(v ?? 0);
    const collectNoVariant = (row) =>
      (row?.attribute_lines || [])
        .filter((l) => l.create_variant === "no_variant")
        .flatMap((l) => l.selected_attribute_value_ids || [])
        .map(Number)
        .filter(Boolean);

    let pairPrice = 0;

    if (isSplit) {
      const left = this._findRowBySide("left") || main;
      const right = this._findRowBySide("right");
      pairPrice =
        n(left?.price ?? left?.list_price) +
        n(right?.price ?? right?.list_price);
      main.no_variant_extra_ids = right ? collectNoVariant(right) : [];
    } else {
      // shared / hybrid: one unit shown in UI; a pair is 2x
      const unit = n(main?.price ?? main?.list_price);
      pairPrice = unit * 2;
    }

    if (Number.isFinite(pairPrice) && pairPrice >= 0) {
      main.price_unit_override = pairPrice; // allow 0.00; forbid negatives
    }

    // 4) Optional products
    const optionalProducts = isSplit
      ? [] // consolidate into main line for split mode
      : this.state.products.filter(
          (p) => p.product_tmpl_id !== this.env.mainProductTmplId
        );

    // 5) Save & close
    console.log("[onConfirm] saving", {
      mode,
      uom_qty: main.product_uom_qty,
      uom: main.product_uom,
      price_unit_override: main.price_unit_override,
    });

    const leftRow = this._findRowBySide("left") || main;
    const rightRow = this._findRowBySide("right");
    // main.line_description = this._buildSOLName({ mode, main, leftRow, rightRow });
    main.line_description = this._buildSOLName({
      mode,
      main,
      leftRow,
      rightRow,
      bullets: true,
    });

    try {
      await this.props.save(main, optionalProducts, this.state.extraProducts);
    } finally {
      this.props.close();
    }
  },
  
});
