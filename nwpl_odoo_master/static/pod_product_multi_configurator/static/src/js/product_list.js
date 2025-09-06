/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductList } from "@sale_product_configurator/js/product_list/product_list";
import { formatCurrency } from "@web/core/currency";

patch(ProductList, {
    props: {
        ...ProductList.props, 
        qtyMode: { type: Boolean, optional: true }, 
    },
    defaultProps: {
        ...ProductList.defaultProps, 
        qtyMode: false, 
    },
});

patch(ProductList.prototype, {
    getFormattedTotal() {
        const items = this.props.areProductsOptional
            ? this.props.products
            : this.props.products.filter(
                  (p) => p.product_tmpl_id === this.env.mainProductTmplId
              );

        const seen = new Set();
        const sum = items.reduce((acc, p) => {
            const isMain = p.product_tmpl_id === this.env.mainProductTmplId;
            const isRight = (p._side || "left") === "right";
            const saved = Number(p._combined_price || 0);

            if (isMain && saved > 0) {
                // Count a saved combined price once for the template (use left row)
                if (!isRight && !seen.has(p.product_tmpl_id)) {
                    seen.add(p.product_tmpl_id);
                    return acc + saved;
                }
                return acc; // skip right side when saved is present
            }

            const unit = Number(p.price ?? p.list_price ?? 0);
            const qty  = Number(p.quantity || 1);
            return acc + unit * qty;
        }, 0);

        // const sum = items.reduce((acc, p) => {
        //     const unit = Number(p.price ?? p.list_price ?? 0);
        //     const qty  = Number(p.quantity || 1);
        //     return acc + unit * qty;
        // }, 0);

        return formatCurrency(sum, this.env.currencyId);
    },
});

// patch(ProductList, (T) => {
//   T.props = Object.assign({}, T.props, {
//     qtyMode: { type: Boolean, optional: true },
//   });

//   T.defaultProps = Object.assign({}, T.defaultProps || {}, {
//     qtyMode: false,
//   });
// });
