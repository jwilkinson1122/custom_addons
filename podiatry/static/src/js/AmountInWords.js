odoo.define('point_of_sale.AmountInWords', function (require) {
    'use strict';

    const {useRef, onMounted} = owl.hooks;
    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');


    class AmountInWords extends PosComponent {
        constructor() {
            super(...arguments);
            this.amount = this.props.amount;
            this.currency_id = this.props.currency_id;
            this.AmountInWordsRef = useRef('amount-in-words');
            onMounted(() => this.renderAmountInWords());
        }

        renderAmountInWords() {
            const self = this;
            try {
                rpc.query({
                    model: 'res.currency',
                    method: 'amount_to_text',
                    args: [this.currency_id, this.amount]
                }).then(function (result) {
                    self.AmountInWordsRef.el.innerText = result;
                })
            } catch (e) {
            }
        }
    }

    AmountInWords.template = 'AmountInWords';

    Registries.Component.add(AmountInWords);

    return AmountInWords;
});
