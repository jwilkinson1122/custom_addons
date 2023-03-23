odoo.define('pod_erp.Main_Page_Buttons', function (require) {

    var gui = require('point_of_sale.Gui');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');

    //-----------------------------------------
    //-----------------------------------------
    // Prescription Button on Main Page
    //-----------------------------------------
    //-----------------------------------------
    class PrescriptionHistoryButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.button_click);
        }
        button_click() {
            this.showScreen('PrescriptionListScreenWidget', { all_orders: this.env.pos.podiatry.all_orders });
        }
    }
    PrescriptionHistoryButton.template = 'PrescriptionHistoryButtons';
    ProductScreen.addControlButton({
        component: PrescriptionHistoryButton,
        condition: function () {
            return true;
        },
        position: ['before', 'SelectGlassesButton'],
    });

    Registries.Component.add(PrescriptionHistoryButton);


    //-----------------------------------------
    //-----------------------------------------
    // Prescription Button on Main Page
    //-----------------------------------------
    //-----------------------------------------


    class PrescriptionButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.button_click);
        }
        button_click() {
            self = this
            self.showPopup('PrescriptionCreationWidget');
        }
    }
    PrescriptionButton.template = 'PrescriptionButton';
    ProductScreen.addControlButton({
        component: PrescriptionButton,
        condition: function () {
            return true;
        },
        position: ['before', 'PrescriptionHistoryButton'],
    });

    Registries.Component.add(PrescriptionButton);

    //-----------------------------------------
    //-----------------------------------------
    // Select Glasses Button on Main Page
    //-----------------------------------------
    //-----------------------------------------


    class SelectGlassesButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.button_click);
        }
        button_click() {
            var self = this;
            if (this.env.pos.get_order().attributes.client)
                this.patient = this.env.pos.get_order().attributes.client.name;
            else
                this.patient = false;
            if (this.env.pos.get_order().podiatry_reference != undefined)
                this.podiatry_reference = this.env.pos.get_order().podiatry_reference.name;
            else
                this.podiatry_reference = false;

            if (!this.patient || !this.podiatry_reference) {
                self.showPopup('ErrorPopup', {
                    title: this.env._t('No patient or Prescription found'),
                    body: this.env._t('You need to select patient & Prescription to continue'),
                });
            }
            else
                self.showPopup('OrderCreationWidget');;
        }
    }
    SelectGlassesButton.template = 'SelectGlassesButton';
    ProductScreen.addControlButton({
        component: SelectGlassesButton,
        condition: function () {
            return true;
        },
        position: ['before', 'PrescriptionHistoryButton'],
    });

    Registries.Component.add(SelectGlassesButton);
    return PrescriptionHistoryButton, PrescriptionButton, SelectGlassesButton;
});