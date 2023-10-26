odoo.define("prescription/static/src/js/prescription_model_extension.js", function (require) {
    "use strict";

    const ActionModel = require("web.ActionModel");

    class PrescriptionModelExtension extends ActionModel.Extension {

        //---------------------------------------------------------------------
        // Public
        //---------------------------------------------------------------------

        /**
         * @override
         * @returns {any}
         */
        get(property) {
            switch (property) {
                case "domain": return this.getDomain();
                case "userId": return this.state.userId;
            }
        }

        /**
         * @override
         */
        async load() {
            await this._updateLocationId();
        }

        /**
         * @override
         */
        prepareState() {
            Object.assign(this.state, {
                locationId: null,
                userId: null,
            });
        }

        //---------------------------------------------------------------------
        // Actions / Getters
        //---------------------------------------------------------------------

        /**
         * @returns {Array[] | null}
         */
        getDomain() {
            if (this.state.locationId) {
                return [["is_available_at", "in", [this.state.locationId]]];
            }
            return null;
        }

        /**
         * @param {number} locationId
         * @returns {Promise}
         */
        setLocationId(locationId) {
            this.state.locationId = locationId;
            this.env.services.rpc({
                route: "/prescription/user_location_set",
                params: {
                    context: this.env.session.user_context,
                    location_id: this.state.locationId,
                    user_id: this.state.userId,
                },
            });
        }

        /**
         * @param {number} userId
         * @returns {Promise}
         */
        updateUserId(userId) {
            this.state.userId = userId;
            this.shouldLoad = true;
        }

        //---------------------------------------------------------------------
        // Private
        //---------------------------------------------------------------------

        /**
         * @returns {Promise}
         */
        async _updateLocationId() {
            this.state.locationId = await this.env.services.rpc({
                route: "/prescription/user_location_get",
                params: {
                    context: this.env.session.user_context,
                    user_id: this.state.userId,
                },
            });
        }
    }

    ActionModel.registry.add("Prescription", PrescriptionModelExtension, 20);

    return PrescriptionModelExtension;
});
