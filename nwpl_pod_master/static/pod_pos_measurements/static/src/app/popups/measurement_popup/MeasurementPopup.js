/** @odoo-module */
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { renderToElement } from "@web/core/utils/render";
import { useService } from "@web/core/utils/hooks";
import { useState, onMounted, onWillUnmount } from "@odoo/owl";
import { PosDB } from "@point_of_sale/app/store/db";
import { DatePickerPopup } from "@nwpl_pod_master/static/pod_pos_measurements/app/popups/date_picker_popup/DatePickerPopup";


class BaseMeasurementPopup extends AbstractAwaitablePopup {
    setup() {
        try {
            super.setup();
            this.pos = usePos();
            this.rpc = useService('rpc');
            this.orm = useService("orm");
            this.popup = useService("popup");
            this.db = new PosDB();

            this.state = useState({
                measurementDate: this._today(),
                filtered_categories: this.getCategoriesWithMeasurementTypes(),
                selected_measurement_types: [],
                measurement_ids: [],
                selected_category: null, // Track the selected category
            });

            Object.assign(this, this.props.info);

            onMounted(this.loadMeasurementLines.bind(this));
            onWillUnmount(this._cleanup.bind(this));
        } catch (error) {
            console.error("Error in setup: ", error);
        }
    }

    _today() {
        return new Date().toISOString().split("T")[0];
    }

    async openDatePicker() {
        try {
            const { confirmed, payload } = await this.popup.add(DatePickerPopup, { title: "Select Measurement Date" });
            if (confirmed) {
                this.state.measurementDate = payload;
            }
        } catch (error) {
            console.error("Error in openDatePicker: ", error);
        }
    }

    getCategoriesWithMeasurementTypes() {
        try {
            const categories = this.pos.db.category_by_id;
            const measurement_types_by_id = this.pos.db.measurement_types_by_id;
            if (!categories || !measurement_types_by_id) {
                console.error("Categories or measurement types are not defined");
                return [];
            }
            return Object.values(categories).filter(category => {
                const measurement_type_ids = category.measurement_type_ids;
                return Array.isArray(measurement_type_ids) && measurement_type_ids.some(id => measurement_types_by_id.hasOwnProperty(id));
            });
        } catch (error) {
            console.error("Error in getCategoriesWithMeasurementTypes: ", error);
            return [];
        }
    }

    async _oncategory(ev) {
        try {
            const cat_id = parseInt(ev.currentTarget.value, 10);
            if (cat_id) {
                this._updateCategory(cat_id);
            } else {
                $(".measurement_create_table").find(".measurement_create_table_right").html('');
            }
        } catch (error) {
            console.error("Error in _oncategory: ", error);
        }
    }

    _updateCategory(cat_id) {
        try {
            const category = this.pos.db.get_category_by_id(cat_id);
            if (category && category.measurement_unit) {
                $(".measurement_create_table").find("select[name='Unit_name']").val(category.measurement_unit[0]);
            }

            const measurement_types = category.measurement_type_ids.map(id => this.pos.db.get_measurement_types_by_id(id)).filter(Boolean);
            this.state.selected_measurement_types = measurement_types;
            this.state.selected_category = category; // Update the selected category

            const rendered_measurement_lines = renderToElement('pod_pos_measurements.DisplayMeasurementTypeInput', { props: { measurement_types: measurement_types } });
            $(".measurement_create_table").find(".measurement_create_table_right").html(rendered_measurement_lines);
        } catch (error) {
            console.error("Error in _updateCategory: ", error);
        }
    }

    async _fetchMeasurements(partner_id) {
        try {
            if (!partner_id) {
                throw new Error("Partner ID is null or undefined.");
            }
            const measurement_data = await this.orm.call("res.partner", "get_measurements", [partner_id]);
            console.log("Fetched measurement data:", measurement_data);
            return measurement_data.map(m => ({
                id: m.id,
                date: m.date,
                category: m.category, // Ensure category name is correctly assigned
                unit: m.unit,
                values: m.values.filter(value => value.value !== false && value.value !== undefined && value.value !== '')
            }));
        } catch (error) {
            console.error("Error in _fetchMeasurements: ", error);
            return [];
        }
    }

    async loadMeasurementLines(measurements) {
        try {
            if (!measurements) {
                const partner_id = this.props.partner ? this.props.partner.id : null;
                console.log("Fetching measurements for partner ID:", partner_id);
                if (partner_id) {
                    measurements = await this._fetchMeasurements(partner_id);
                }
            }

            if (measurements) {
                console.log("Measurements found:", measurements);
                this._renderMeasurementLines(measurements);
            } else {
                console.error("No measurements found for partner.");
            }
        } catch (error) {
            console.error("Error in loadMeasurementLines: ", error);
        }
    }

    _renderMeasurementLines(measurements) {
        try {
            const rendered_measurement_lines = renderToElement('pod_pos_measurements.DisplayMeasurementLines', {
                props: { measurements: measurements, deleteMeasurement: this.deleteMeasurement.bind(this) }
            });
            $(".pos_measurements_table").html(rendered_measurement_lines);
        } catch (error) {
            console.error("Error in _renderMeasurementLines: ", error);
        }
    }

    async deleteMeasurement(measurement_id) {
        try {
            console.log(`Attempting to delete measurement with ID: ${measurement_id}`);
            const result = await this.orm.call('res.partner', 'delete_measurement', [[measurement_id]]);
            if (result.success) {
                console.log(`Successfully deleted measurement with ID: ${measurement_id}`);
                this.loadMeasurementLines();
                this.popup.add(ConfirmPopup, { title: "Success", body: result.message });
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error(`Error deleting measurement with ID: ${measurement_id}: ${error.message}`);
            this.popup.add(ErrorPopup, { title: "Delete Failed", body: error.message });
        }
    }

    _AddMeasurementlines() {
        try {
            this.loadMeasurementLines();
            this.toggleMeasurementLinesVisibility(true);
        } catch (error) {
            console.error("Error in _AddMeasurementlines: ", error);
        }
    }

    _hideMeasurementlines() {
        try {
            this.toggleMeasurementLinesVisibility(false);
            $(".pos_measurements_table").html('');
        } catch (error) {
            console.error("Error in _hideMeasurementlines: ", error);
        }
    }

    clearMeasurementForm() {
        try {
            $(".measurement_create_table").find("input, select").val('');
            $(".measurement_create_table_right").html('');
        } catch (error) {
            console.error("Error in clearMeasurementForm: ", error);
        }
    }

    toggleMeasurementLinesVisibility(show) {
        try {
            $(".hidemeasurementlinesbtn")[0].style.display = show ? 'block' : 'none';
            $(".addmeasurementlinesbtn")[0].style.display = show ? 'none' : 'block';
        } catch (error) {
            console.error("Error in toggleMeasurementLinesVisibility: ", error);
        }
    }

    async confirm() {
        try {
            const error = this._validateForm();
            if (error) {
                this.popup.add(ErrorPopup, { title: "Invalid Data", body: error });
                return;
            }
    
            const desc = this._prepareMeasurementDesc();
            console.log('Prepared Measurement Description:', desc);
            console.log('Calling _addMeasurement with:', desc);
    
            try {
                await this._addMeasurement(desc.partner_id, desc.measurement_values, desc.sale_order_id);
                await this._updatePartnerMeasurements(desc.partner_id);
                this.clearMeasurementForm();
                await this.loadMeasurementLines();
                this.toggleMeasurementLinesVisibility(true);
                this.popup.add(ConfirmPopup, { title: "Success", body: "Measurements added successfully." });
            } catch (error) {
                this.popup.add(ErrorPopup, { title: "RPC Call Failed", body: error.message });
            }
        } catch (error) {
            console.error("Error in confirm: ", error);
        }
    }

    _prepareMeasurementDesc() {
        try {
            const partner_id = this.props.partner ? this.props.partner.id : null;
            const sale_order_id = this.props.sale_order_id || null;
            const date = this.state.measurementDate;
            const category_id = parseInt($(".measurement_create_table").find("select[name='category_name']").val(), 10);
            const unit_id = parseInt($(".measurement_create_table").find("select[name='Unit_name']").val(), 10);
            const measurement_types = $(".measurement_create_table").find(".measurement_type_input_cl");

            const mtypes = $.map(measurement_types, function (el) {
                const measurement_value = parseFloat($(el).val());
                return {
                    'measurement_type': parseInt($(el).attr('name'), 10),
                    'measurement': !isNaN(measurement_value) ? measurement_value : null,
                };
            }).filter(item => item.measurement !== null);

            return {
                partner_id: partner_id,
                sale_order_id: sale_order_id, // Include sale_order_id
                measurement_values: [{
                    'date': date,
                    'category_id': category_id,
                    'measurement_unit': unit_id,
                    'measurement_ids': mtypes,
                }]
            };
        } catch (error) {
            console.error("Error in _prepareMeasurementDesc: ", error);
            return {};
        }
    }

    async _addMeasurement(partner_id, measurement_values, sale_order_id = null) {
        try {
            if (partner_id && measurement_values && measurement_values.length > 0) {
                console.log('Sending to backend:', partner_id, measurement_values); // Log the data being sent
                if (sale_order_id) {
                    return this.orm.call('sale.order', 'add_measurement', [sale_order_id, measurement_values]);
                } else {
                    return this.orm.call('res.partner', 'add_measurement', [partner_id, measurement_values]);
                }
            }
            throw new Error('No partner ID or measurement values provided');
        } catch (error) {
            console.error("Error in _addMeasurement: ", error);
        }
    }

    async _updatePartnerMeasurements(partner_id) {
        try {
            const measurement_ids = await this.orm.call('res.partner', 'get_measurements', [partner_id]);
            this.pos.db.partner_by_id[partner_id].measurement_ids = measurement_ids.map(m => m.id);
        } catch (error) {
            console.error("Error in _updatePartnerMeasurements: ", error);
        }
    }

    _validateForm() {
        try {
            const date = this.state.measurementDate;
            const category_id = parseInt($(".measurement_create_table").find("select[name='category_name']").val(), 10);
            const unit_id = parseInt($(".measurement_create_table").find("select[name='Unit_name']").val(), 10);
            const measurement_types = $(".measurement_create_table").find(".measurement_type_input_cl");

            if (!date) {
                return "Please enter a valid date";
            } else if (!category_id) {
                return "Please select categories";
            } else if (!unit_id) {
                return "Please select a measurement unit";
            }

            const mtypes = $.map(measurement_types, function (el) {
                const measurement_value = parseFloat($(el).val());
                return {
                    'measurement_type': parseInt($(el).attr('name'), 10),
                    'measurement': !isNaN(measurement_value) ? measurement_value : null,
                };
            }).filter(item => item.measurement !== null);

            if (mtypes.length === 0) {
                return "Please enter at least one measurement value.";
            }

            return "";
        } catch (error) {
            console.error("Error in _validateForm: ", error);
            return "An error occurred during form validation.";
        }
    }

    _cleanup() {
        try {
            console.log("Cleaning up MeasurementPopup");
        } catch (error) {
            console.error("Error in _cleanup: ", error);
        }
    }
}

export class MeasurementPopup extends BaseMeasurementPopup {
    static template = "pod_pos_measurements.MeasurementPopup";

    static defaultProps = {
        title: 'Confirm ?',
        value: ''
    };

    setup() {
        try {
            super.setup();
            if (this.props.product) {
                this.props.image_url = this._getProductImageUrl(this.props.product);
            }
            onMounted(this._onMounted.bind(this));
        } catch (error) {
            console.error("Error in setup: ", error);
        }
    }

    _onMounted() {
        try {
            $('.tab-link:first-child').addClass('text-primary');
        } catch (error) {
            console.error("Error in _onMounted: ", error);
        }
    }

    _getProductImageUrl(product) {
        try {
            return `${window.location.origin}/web/image?model=product.product&field=image_128&id=${product.id}`;
        } catch (error) {
            console.error("Error in _getProductImageUrl: ", error);
            return '';
        }
    }

    pod_add_measurement(event) {
        try {
            const measurement_list = $('.pod_checked_measurement:checked').map((_, element) => $(element).data('id')).get();
            const line = this.props.line;

            if (line) {
                line.pod_measurement_ids = measurement_list;
                line.is_extra_price_set = measurement_list.length === 0;
                line.set_unit_price(line.price);

                if (this.env && this.env.pos && this.env.pos.get_order()) {
                    this.env.pos.get_order().save_to_db();
                }
            } else {
                // If no line, just update the measurements
                console.log("No line found in props, updating measurements");
                this.loadMeasurementLines();
            }

            this.cancel();
        } catch (error) {
            console.error("Error in pod_add_measurement: ", error);
        }
    }

    pod_change_tab(event) {
        try {
            const content_div_id = $(event.target).data('id');
            if (content_div_id) {
                $('.tab-content').removeClass('current');
                $('.tab-link').removeClass('current text-primary');
                $(event.currentTarget).addClass('text-primary');
                $(content_div_id).addClass('current');
            }
        } catch (error) {
            console.error("Error in pod_change_tab: ", error);
        }
    }
}

export class SetMeasurementPopup extends BaseMeasurementPopup {
    static template = "pod_pos_measurements.SetMeasurementPopup";

    static defaultProps = {
        confirmKey: false,
        title: "Set Measurement",
        confirmText: "Confirm",
        cancelText: "Cancel"
    };

    setup() {
        try {
            super.setup();
            this.state = useState({
                measurements: [],
                selectedMeasurements: new Set(),
                noMeasurementsAvailable: false,
            });
            console.log("SetMeasurementPopup props:", this.props); // Log the props
            Object.assign(this, this.props.info);
            onMounted(this.loadMeasurements.bind(this));
            onWillUnmount(this.cleanup.bind(this));
        } catch (error) {
            console.error("Error in setup: ", error);
        }
    }

    async loadMeasurements() {
        try {
            if (!this.props.partner || !this.props.partner.id) {
                throw new Error("Partner ID is null or undefined.");
            }
            const partner_measurements = await this.orm.call("res.partner", "get_measurements", [this.props.partner.id]);
            this.state.measurements = partner_measurements || [];
            if (this.state.measurements.length === 0) {
                this.state.noMeasurementsAvailable = true;
            } else {
                this.state.noMeasurementsAvailable = false;
            }
        } catch (error) {
            console.error("Error in loadMeasurements: ", error);
            this.state.noMeasurementsAvailable = true;
        }
    }

    toggleMeasurementSelection(ev) {
        try {
            const measurementId = parseInt(ev.target.value, 10);
            const measurementCat = this.state.measurements.find(cat => cat.id === measurementId);
            if (!measurementCat) {
                console.error("Measurement category not found:", measurementId);
                return;
            }
            if (ev.target.checked) {
                this.state.selectedMeasurements.add(measurementId);
                measurementCat.values.forEach(measurement => {
                    this.state.selectedMeasurements.add(measurement.id);
                });
            } else {
                this.state.selectedMeasurements.delete(measurementId);
                measurementCat.values.forEach(measurement => {
                    this.state.selectedMeasurements.delete(measurement.id);
                });
            }
        } catch (error) {
            console.error("Error in toggleMeasurementSelection: ", error);
        }
    }

    async confirm() {
        try {
            if (this.state.selectedMeasurements.size === 0) {
                throw new Error("No measurement selected.");
            }

            const measurement_ids = Array.from(this.state.selectedMeasurements).map(id => this.pos.db.get_measurement_by_id(id));
            const selected_orderline = this.pos.get_order().get_selected_orderline();
            if (!selected_orderline) {
                throw new Error("No order line selected.");
            }

            selected_orderline.set_measurement_ids(measurement_ids);
            selected_orderline.set_measurement_unit(measurement_ids[0]?.unit);
            const { confirmed } = await this.popup.add(ConfirmPopup, { title: "Success", body: "Measurements set successfully." });

            if (confirmed) {
                this.cancel(); // Close the SetMeasurementPopup
            }
        } catch (error) {
            this.pos.popup.add(ErrorPopup, { title: "Measurement Error", body: error.message });
        }
    }

    async skip() {
        try {
            this.cancel(); // Close the SetMeasurementPopup without setting measurements
        } catch (error) {
            console.error("Error in skip: ", error);
        }
    }


    cleanup() {
        try {
            console.log("Cleaning up SetMeasurementPopup");
            this.state.selectedMeasurements.clear();
            this.state.measurements = [];
        } catch (error) {
            console.error("Error in cleanup: ", error);
        }
    }
}

