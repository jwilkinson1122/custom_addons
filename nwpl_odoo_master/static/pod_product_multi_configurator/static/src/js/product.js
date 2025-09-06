/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { Product } from "@sale_product_configurator/js/product/product";
import { formatCurrency } from "@web/core/currency";

patch(Product, (T) => {
  // Extend, don’t replace, and keep existing descriptors intact.
  T.props = Object.assign({}, T.props, {
    length: { type: Number, optional: true },
    qtyMode: { type: Boolean, optional: true },
  });

  // Guard against undefined defaultProps (don’t spread undefined).
  T.defaultProps = Object.assign({}, T.defaultProps || {}, {
    qtyMode: false,
  });
});

patch(Product.prototype, {
  setup() {
    super.setup();
    this.orm = useService("orm");
    this.notification = useService("notification");
  },

  _fmt(amount) {
    return formatCurrency(Number(amount || 0), this.env.currencyId);
  },

  _displayName() {
    const name = this.props.display_name || this.props.name || "";
    if (this.props._side === "left") return `${name} — Left`;
    if (this.props._side === "right") return `${name} — Right`;
    return name;
  },

  _displayPrice() {
    const unit = Number(this.props.price ?? this.props.list_price ?? 0);
    const qty = Number(this.props.quantity || 1);
    const isMain = this.props.product_tmpl_id === this.env.mainProductTmplId;
    const isSplit = !!this.env.laterality?.isGlobalSplit?.();
    const isLeft = (this.props._side || "left") === "left";

    // Prefer the saved (confirmed) SOL price when present (edit mode)
    if (
      isMain &&
      isSplit &&
      Number(this.props._combined_price || 0) > 0 &&
      isLeft
    ) {
      return this._fmt(this.props._combined_price);
    }

    // Bilateral Split: render only on the left row
    if (isMain && isSplit && isLeft) {
      const twin = Number(this.props._twin_price ?? 0);
      if (twin > 0) {
        const equal = Math.abs(twin - unit) < 0.005;
        const sum = unit + twin;
        return equal
          ? `${this._fmt(unit)} × 2 = ${this._fmt(sum)}`
          : `${this._fmt(unit)} + ${this._fmt(twin)} = ${this._fmt(sum)}`;
      }
      return this._fmt(unit);
    }

    // Bilateral Shared (single row): show unit × qty
    if (isMain && !isSplit && qty >= 2) {
      return `${this._fmt(unit)} × ${qty} = ${this._fmt(unit * qty)}`;
    }

    // Everything else (right row, optional lines, non-bilateral)
    return this._fmt(unit);
  },

  get showPrice() {
    return this._displayPrice();
  },

  _isBilateral() {
    return !!(
      this.env.laterality && this.env.laterality.mode() === "bilateral"
    );
  },

  _qtyStep() {
    return this._isBilateral() ? 2 : 1;
  },

  _qtyMin() {
    // For the main (non-optional) product, keep a sensible minimum (2 for bilateral, 1 otherwise).
    // Optional lines can still go to 0 if Odoo allows it.
    if (this.props.optional) return 0;
    return this._isBilateral() ? 2 : 1;
  },

  increaseQuantity() {
    const step = this._qtyStep();
    const current = Number(this.props.quantity || 0);
    const next = Math.max(this._qtyMin(), current + step);
    this.env.setQuantity(this.props.product_tmpl_id, next);
  },

  decreaseQuantity() {
    const step = this._qtyStep();
    const current = Number(this.props.quantity || 0);
    const next = Math.max(this._qtyMin(), current - step);
    this.env.setQuantity(this.props.product_tmpl_id, next);
  },

  async togglePreferred({ side = "shared", line, value }) {
    try {
      // Partner id: use what you pass to the dialog (see step 3)
      const partnerId =
        this.props.partnerId ||
        this.env?.dialog?.props?.partnerId ||
        this.props.context?.partner_id;

      if (!partnerId) {
        this.notification.add(
          this.env._t("Missing partner to save preference."),
          { type: "warning" }
        );
        return;
      }

      // Decide current → desired flag
      const current =
        side === "left"
          ? !!value.isPreferredLeft
          : side === "right"
          ? !!value.isPreferredRight
          : !!value.isPreferred;
      const desired = !current;

      // We usually only have the PTAV id in the UI.
      // Backend should accept ptav_id OR pav_id (see note below).
      await this.orm.call(
        "product.config.preference",
        "toggle_preference",
        [],
        {
          partner_id: partnerId,
          product_tmpl_id: this.props.product_tmpl_id,
          attribute_id: Number(line.attribute_id || line.id),
          ptav_id: Number(value.id), // <-- send PTAV; backend resolves to PAV
          scope: side, // 'left' | 'right' | 'shared'
          preferred: desired,
        }
      );

      // Optimistic UI flip
      if (side === "left") value.isPreferredLeft = desired;
      else if (side === "right") value.isPreferredRight = desired;
      else value.isPreferred = desired;

      this.render(true);
    } catch (e) {
      this.notification.add(this.env._t("Could not update preference."), {
        type: "danger",
      });
      throw e;
    }
  },
});
