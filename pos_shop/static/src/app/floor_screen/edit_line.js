/** @odoo-module */

import { Component, useExternalListener, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class EditLine extends Component {
    static template = "pos_shop.EditLine";
    static props = {
        selectedSections: Object,
        nbrFloors: Number,
        floorMapScrollTop: Number,
        isColorPicker: Boolean,
        toggleColorPicker: Function,
        createSection: Function,
        duplicateSectionOrFloor: Function,
        renameSection: Function,
        changeSeatsNum: Function,
        changeToCircle: Function,
        changeToSquare: Function,
        setSectionColor: Function,
        setFloorColor: Function,
        deleteFloorOrSection: Function,
        toggleEditMode: Function,
    };

    setup() {
        this.ui = useState(useService("ui"));
        useExternalListener(window, "click", this.onOutsideClick);
    }

    onOutsideClick() {
        if (this.props.isColorPicker) {
            this.props.isColorPicker = false;
        }
    }

    getSelectedSectionsShape() {
        let shape = "round";
        this.props.selectedSections.forEach((section) => {
            if (section.shape == "square") {
                shape = "square";
            }
        });
        return shape;
    }
}
