import { toRaw } from '@odoo/owl';
import { registry } from "@web/core/registry";
import { TaxTotalsComponent } from "../../../../account/static/src/components/tax_totals/tax_totals";

export class CustomTaxTotalComponent extends TaxTotalsComponent {
    static template = "custom_sale.custom_sale_total_tax"; // View name
    // static components = { TaxGroupComponent };
    /* static props = {
        ...standardFieldProps,
    }; */

    constructor() {
        super(...arguments);
    }

    // @useEffect(() => {

    // }, []);


    setup() {
        super.setup();
        console.log('------------- setup -------------');
        console.log('Props = ', this.props);
        this.formatData(this.props);

        console.log(this.totals);
    }

    formatData(props) {
        let totals = JSON.parse(JSON.stringify(toRaw(props.record.data[this.props.name])));
        if (!totals) {
            return;
        }
        totals.total_amount_currency = (Math.floor(totals.total_amount_currency * 10) / 10)
        this.totals = totals;

        console.log('Total Custom = ', this.totals);

    }

    _onChangeTaxValueByTaxGroup({ oldValue, newValue }) {
        console.log('_onChangeTaxValueByTaxGroup');

        if (oldValue === newValue) return;
        this.props.record.update({ [this.props.name]: this.totals });
        delete this.totals.cash_rounding_base_amount_currency;
    }

}

export const customTaxTotalsComponent = {
    component: CustomTaxTotalComponent,
};

registry.category("modals").add("custom_account_tax_totals_field", customTaxTotalsComponent);

