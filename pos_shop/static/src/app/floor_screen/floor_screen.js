/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";
import { ConnectionLostError } from "@web/core/network/rpc_service";
import { debounce } from "@web/core/utils/timing";
import { registry } from "@web/core/registry";

import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

import { EditSection } from "@pos_shop/app/floor_screen/edit_section";
import { EditLine } from "@pos_shop/app/floor_screen/edit_line";
import { Section } from "@pos_shop/app/floor_screen/section";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import {
    Component,
    onPatched,
    onMounted,
    onWillUnmount,
    useRef,
    useState,
    onWillStart,
} from "@odoo/owl";

export class FloorScreen extends Component {
    static components = { EditSection, EditLine, Section };
    static template = "pos_shop.FloorScreen";
    static props = { isShown: Boolean, floor: { type: true, optional: true } };
    static storeOnOrder = false;

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
        this.orm = useService("orm");
        const floor = this.pos.currentFloor;
        this.state = useState({
            selectedFloorId: floor ? floor.id : null,
            selectedSectionIds: [],
            floorBackground: floor ? floor.background_color : null,
            floorMapScrollTop: 0,
            isColorPicker: false,
        });
        const ui = useState(useService("ui"));
        const mode = localStorage.getItem("floorPlanStyle");
        this.pos.floorPlanStyle = ui.isSmall || mode == "kanban" ? "kanban" : "default";
        this.floorMapRef = useRef("floor-map-ref");
        this.addFloorRef = useRef("add-floor-ref");
        this.map = useRef("map");
        onPatched(this.onPatched);
        onMounted(this.onMounted);
        onWillUnmount(this.onWillUnmount);
        onWillStart(this.onWillStart);
    }
    onPatched() {
        this.floorMapRef.el.style.background = this.state.floorBackground;
        if (!this.pos.isEditMode && this.pos.floors.length > 0) {
            this.addFloorRef.el.style.display = "none";
        } else {
            this.addFloorRef.el.style.display = "initial";
        }
        this.state.floorMapScrollTop = this.floorMapRef.el.getBoundingClientRect().top;
    }
    async onWillStart() {
        const section = this.pos.section;
        if (section) {
            const orders = this.pos.get_order_list();
            const sectionOrders = orders.filter(
                (order) => order.sectionId === section.id && !order.finalized
            );
            const qtyChange = sectionOrders.reduce(
                (acc, order) => {
                    const quantityChange = order.getOrderChanges();
                    const quantitySkipped = order.getOrderChanges(true);
                    acc.changed += quantityChange.count;
                    acc.skipped += quantitySkipped.count;
                    return acc;
                },
                { changed: 0, skipped: 0 }
            );

            section.changes_count = qtyChange.changed;
            section.skip_changes = qtyChange.skipped;
        }
        await this.pos.unsetSection();
    }
    onMounted() {
        this.pos.openCashControl();
        this.floorMapRef.el.style.background = this.state.floorBackground;
        if (!this.pos.isEditMode && this.pos.floors.length > 0) {
            this.addFloorRef.el.style.display = "none";
        } else {
            this.addFloorRef.el.style.display = "initial";
        }
        this.state.floorMapScrollTop = this.floorMapRef.el.getBoundingClientRect().top;
    }
    onWillUnmount() {
        clearInterval(this.sectionLongpolling);
    }
    _computePinchHypo(ev, callbackFunction) {
        const touches = ev.touches;
        // If two pointers are down, check for pinch gestures
        if (touches.length === 2) {
            const deltaX = touches[0].pageX - touches[1].pageX;
            const deltaY = touches[0].pageY - touches[1].pageY;
            callbackFunction(Math.hypot(deltaX, deltaY));
        }
    }
    _onPinchStart(ev) {
        ev.currentTarget.style.setProperty("touch-action", "none");
        this._computePinchHypo(ev, this.startPinch.bind(this));
    }
    _onPinchEnd(ev) {
        ev.currentTarget.style.removeProperty("touch-action");
    }
    _onPinchMove(ev) {
        debounce(this._computePinchHypo, 10, true)(ev, this.movePinch.bind(this));
    }
    _onDeselectSection() {
        this.state.selectedSectionIds = [];
    }
    async _createSectionHelper(copySection, duplicateFloor = false) {
        const existingSection = this.activeFloor.sections;
        let newSection;
        if (copySection) {
            newSection = Object.assign({}, copySection);
            if (!duplicateFloor) {
                newSection.position_h += 10;
                newSection.position_v += 10;
            }
            delete newSection.id;
            newSection.order_count = 0;
        } else {
            let posV = 0;
            let posH = 10;
            const referenceScreenWidth = 1180;
            const spaceBetweenSection = 15 * (screen.width / referenceScreenWidth);
            const h_min = spaceBetweenSection;
            const h_max = screen.width;
            const v_max = screen.height;
            let potentialWidth = 100 * (h_max / referenceScreenWidth);
            if (potentialWidth > 130) {
                potentialWidth = 130;
            } else if (potentialWidth < 75) {
                potentialWidth = 75;
            }
            const heightSection = potentialWidth;
            const widthSection = potentialWidth;
            const positionSection = [];

            existingSection.forEach((section) => {
                positionSection.push([
                    section.position_v,
                    section.position_v + section.height,
                    section.position_h,
                    section.position_h + section.width,
                ]);
            });

            positionSection.sort((sectionA, sectionB) => {
                if (sectionA[0] < sectionB[0]) {
                    return -1;
                } else if (sectionA[0] > sectionB[0]) {
                    return 1;
                } else if (sectionA[2] < sectionB[2]) {
                    return -1;
                } else {
                    return 1;
                }
            });

            let actualHeight = 100;
            let impossible = true;

            while (actualHeight <= v_max - heightSection - spaceBetweenSection && impossible) {
                const sectionIntervals = [
                    [h_min, h_min, v_max],
                    [h_max, h_max, v_max],
                ];
                for (let i = 0; i < positionSection.length; i++) {
                    if (positionSection[i][0] >= actualHeight + heightSection + spaceBetweenSection) {
                        continue;
                    } else if (positionSection[i][1] + spaceBetweenSection <= actualHeight) {
                        continue;
                    } else {
                        sectionIntervals.push([
                            positionSection[i][2],
                            positionSection[i][3],
                            positionSection[i][1],
                        ]);
                    }
                }

                sectionIntervals.sort((a, b) => {
                    if (a[0] < b[0]) {
                        return -1;
                    } else if (a[0] > b[0]) {
                        return 1;
                    } else if (a[1] < b[1]) {
                        return -1;
                    } else {
                        return 1;
                    }
                });

                let nextHeight = v_max;
                for (let i = 0; i < sectionIntervals.length - 1; i++) {
                    if (sectionIntervals[i][2] < nextHeight) {
                        nextHeight = sectionIntervals[i][2];
                    }

                    if (
                        sectionIntervals[i + 1][0] - sectionIntervals[i][1] >
                        widthSection + spaceBetweenSection
                    ) {
                        impossible = false;
                        posV = actualHeight;
                        posH = sectionIntervals[i][1] + spaceBetweenSection;
                        break;
                    }
                }
                actualHeight = nextHeight + spaceBetweenSection;
            }

            if (impossible) {
                posV = positionSection[0][0] + 10;
                posH = positionSection[0][2] + 10;
            }

            newSection = {
                position_v: posV,
                position_h: posH,
                width: widthSection,
                height: heightSection,
                shape: "square",
                seats: 2,
                color: "rgb(53, 211, 116)",
            };
        }
        if (!duplicateFloor) {
            newSection.name = this._getNewSectionName();
        }
        newSection.floor_id = [this.activeFloor.id, ""];
        newSection.floor = this.activeFloor;
        await this._save(newSection);
        this.activeSections.push(newSection);
        this.activeFloor.section_ids.push(newSection.id);
        return newSection;
    }
    _getNewSectionName() {
        let firstNum = 1;
        const sectionsNameNumber = this.activeSections
            .map((section) => +section.name)
            .sort(function (a, b) {
                return a - b;
            });

        for (let i = 0; i < sectionsNameNumber.length; i++) {
            if (sectionsNameNumber[i] == firstNum) {
                firstNum += 1;
            } else {
                break;
            }
        }
        return firstNum.toString();
    }
    async _save(section) {
        const sectionCopy = {
            floor_id: section.floor.id,
            color: section.color,
            height: section.height,
            name: section.name,
            position_h: section.position_h,
            position_v: section.position_v,
            seats: section.seats,
            shape: section.shape,
            width: section.width,
        };

        if (section.id) {
            await this.orm.write("shop.section", [section.id], sectionCopy);
        } else {
            const sectionId = await this.orm.create("shop.section", [sectionCopy]);

            section.id = sectionId[0];
            this.pos.sections_by_id[sectionId] = section;
        }
    }
    async _renameFloor(floorId, newName) {
        await this.orm.call("shop.floor", "rename_floor", [floorId, newName]);
    }
    get activeFloor() {
        return this.state.selectedFloorId
            ? this.pos.floors_by_id[this.state.selectedFloorId]
            : null;
    }
    get activeSections() {
        return this.activeFloor ? this.activeFloor.sections : null;
    }
    get isFloorEmpty() {
        return this.activeSections ? this.activeSections.length === 0 : true;
    }
    get selectedSections() {
        const sections = [];
        this.state.selectedSectionIds.forEach((id) => {
            sections.push(this.pos.sections_by_id[id]);
        });
        return sections;
    }
    get nbrFloors() {
        return this.pos.floors.length;
    }
    movePinch(hypot) {
        const delta = hypot / this.scalehypot;
        const value = this.initalScale * delta;
        this.setScale(value);
    }
    startPinch(hypot) {
        this.scalehypot = hypot;
        this.initalScale = this.getScale();
    }
    getScale() {
        const scale = this.map.el.style.getPropertyValue("--scale");
        const parsedScaleValue = parseFloat(scale);
        return isNaN(parsedScaleValue) ? 1 : parsedScaleValue;
    }
    setScale(value) {
        // a scale can't be a negative number
        if (value > 0) {
            this.map.el.style.setProperty("--scale", value);
        }
    }
    selectFloor(floor) {
        this.pos.currentFloor = floor;
        this.state.selectedFloorId = floor.id;
        this.state.floorBackground = this.activeFloor.background_color;
        this.state.selectedSectionIds = [];
    }
    toggleEditMode() {
        this.pos.toggleEditMode();
        if (!this.pos.isEditMode && this.pos.floors.length > 0) {
            this.addFloorRef.el.style.display = "none";
        } else {
            this.addFloorRef.el.style.display = "initial";
        }
        this.state.selectedSectionIds = [];
    }
    async onSelectSection(section, ev) {
        if (this.pos.isEditMode) {
            if (ev.ctrlKey || ev.metaKey) {
                this.state.selectedSectionIds.push(section.id);
            } else {
                this.state.selectedSectionIds = [];
                this.state.selectedSectionIds.push(section.id);
            }
        } else {
            if (this.pos.orderToTransfer) {
                await this.pos.transferSection(section);
            } else {
                try {
                    await this.pos.setSection(section);
                } catch (e) {
                    if (!(e instanceof ConnectionLostError)) {
                        throw e;
                    }
                    // Reject error in a separate stack to display the offline popup, but continue the flow
                    Promise.reject(e);
                }
            }
            const order = this.pos.get_order();
            this.pos.showScreen(order.get_screen_data().name);
        }
    }
    async onSaveSection(section) {
        if (this.pos.sections_by_id[section.id] && this.pos.sections_by_id[section.id].active) {
            await this._save(section);
        }
    }
    async addFloor() {
        const { confirmed, payload: newName } = await this.popup.add(TextInputPopup, {
            title: _t("New Floor"),
            placeholder: _t("Floor name"),
        });
        if (!confirmed) {
            return;
        }
        const floor = await this.orm.call("shop.floor", "create_from_ui", [
            newName,
            "#ACADAD",
            this.pos.config.id,
        ]);
        this.pos.floors_by_id[floor.id] = floor;
        this.pos.floors.push(floor);
        this.selectFloor(floor);
        this.pos.isEditMode = true;
    }
    async createSection() {
        const newSection = await this._createSectionHelper();
        newSection.skip_changes = 0;
        newSection.changes_count = 0;
        newSection.order_count = 0;
        if (newSection) {
            this.state.selectedSectionIds = [];
            this.state.selectedSectionIds.push(newSection.id);
        }
    }
    async duplicateSectionOrFloor() {
        if (this.selectedSections.length == 0) {
            const floor = this.activeFloor;
            const sections = this.activeFloor.sections;
            const newFloorName = floor.name + " (copy)";
            const newFloor = await this.orm.call("shop.floor", "create_from_ui", [
                newFloorName,
                floor.background_color,
                this.pos.config.id,
            ]);
            this.pos.floors_by_id[newFloor.id] = newFloor;
            this.pos.floors.push(newFloor);
            this.selectFloor(newFloor);
            for (const section of sections) {
                await this._createSectionHelper(section, true);
            }
            return;
        }
        const selectedSections = this.selectedSections;
        this._onDeselectSection();

        for (const section of selectedSections) {
            const newSection = await this._createSectionHelper(section);
            if (newSection) {
                this.state.selectedSectionIds.push(newSection.id);
            }
        }
    }
    async renameSection() {
        const selectedSections = this.selectedSections;
        const selectedFloor = this.activeFloor;
        if (selectedSections.length > 1) {
            return;
        }
        if (selectedSections.length == 0) {
            const { confirmed, payload: newName } = await this.popup.add(TextInputPopup, {
                startingValue: selectedFloor.name,
                title: _t("Floor Name ?"),
            });
            if (!confirmed) {
                return;
            }
            if (newName !== selectedFloor.name) {
                selectedFloor.name = newName;
                await this._renameFloor(selectedFloor.id, newName);
            }
            return;
        }
        const selectedSection = selectedSections[0];
        const { confirmed, payload: newName } = await this.popup.add(TextInputPopup, {
            startingValue: selectedSection.name,
            title: _t("Section Name?"),
        });
        if (!confirmed) {
            return;
        }
        if (newName !== selectedSection.name) {
            selectedSection.name = newName;
            await this._save(selectedSection);
        }
    }
    async changeSeatsNum() {
        const selectedSections = this.selectedSections;
        if (selectedSections.length == 0) {
            return;
        }
        const { confirmed, payload: inputNumber } = await this.popup.add(NumberPopup, {
            startingValue: 0,
            cheap: true,
            title: _t("Number of Seats?"),
            isInputSelected: true,
        });
        if (!confirmed) {
            return;
        }
        const newSeatsNum = parseInt(inputNumber, 10);
        selectedSections.forEach(async (selectedSection) => {
            if (newSeatsNum !== selectedSection.seats) {
                selectedSection.seats = newSeatsNum;
                await this._save(selectedSection);
            }
        });
    }
    async changeToCircle() {
        await this.changeShape("round");
    }
    async changeToSquare() {
        await this.changeShape("square");
    }
    async changeShape(form) {
        if (this.selectedSections.length == 0) {
            return;
        }
        this.selectedSections.forEach(async (selectedSection) => {
            selectedSection.shape = form;
            await this._save(selectedSection);
        });
    }
    async setSectionColor(color) {
        const selectedSections = this.selectedSections;
        selectedSections.forEach(async (selectedSection) => {
            selectedSection.color = color;
            await this._save(selectedSection);
        });
        this.state.isColorPicker = false;
    }
    async setFloorColor(color) {
        this.state.floorBackground = color;
        this.activeFloor.background_color = color;
        await this.orm.write("shop.floor", [this.activeFloor.id], {
            background_color: color,
        });
        this.state.isColorPicker = false;
    }
    toggleColorPicker() {
        this.state.isColorPicker = !this.state.isColorPicker;
    }
    async deleteFloorOrSection() {
        if (this.selectedSections.length == 0) {
            const { confirmed } = await this.popup.add(ConfirmPopup, {
                title: `Removing floor ${this.activeFloor.name}`,
                body: sprintf(
                    _t("Removing a floor cannot be undone. Do you still want to remove %s?"),
                    this.activeFloor.name
                ),
            });
            if (!confirmed) {
                return;
            }
            const originalSelectedFloorId = this.activeFloor.id;
            await this.orm.call("shop.floor", "deactivate_floor", [
                originalSelectedFloorId,
                this.pos.pos_session.id,
            ]);
            const floor = this.pos.floors_by_id[originalSelectedFloorId];
            const orderList = [...this.pos.get_order_list()];
            for (const order of orderList) {
                if (floor.section_ids.includes(order.sectionId)) {
                    this.pos.removeOrder(order, false);
                }
            }
            floor.section_ids.forEach((sectionId) => {
                delete this.pos.sections_by_id[sectionId];
            });
            delete this.pos.floors_by_id[originalSelectedFloorId];
            this.pos.floors = this.pos.floors.filter(
                (floor) => floor.id != originalSelectedFloorId
            );
            this.pos.TICKET_SCREEN_STATE.syncedOrders.cache = {};
            if (this.pos.floors.length > 0) {
                this.selectFloor(this.pos.floors[0]);
            } else {
                this.pos.isEditMode = false;
                this.pos.floorPlanStyle = "default";
                this.state.floorBackground = null;
            }
            return;
        }
        const { confirmed } = await this.popup.add(ConfirmPopup, {
            title: _t("Are you sure?"),
            body: _t("Removing a section cannot be undone"),
        });
        if (!confirmed) {
            return;
        }
        const originalSelectedSectionIds = [...this.state.selectedSectionIds];
        const response = await this.orm.call("shop.section", "are_orders_still_in_draft", [
            originalSelectedSectionIds,
        ]);
        if (!response) {
            for (const id of originalSelectedSectionIds) {
                //remove order not send to server
                for (const order of this.pos.get_order_list()) {
                    if (order.sectionId == id) {
                        this.pos.removeOrder(order, false);
                    }
                }
                this.pos.sections_by_id[id].active = false;
                this.orm.write("shop.section", [id], { active: false });
                this.activeFloor.sections = this.activeSections.filter((section) => section.id !== id);
                delete this.pos.sections_by_id[id];
            }
        } else {
            await this.popup.add(ErrorPopup, {
                title: _t("Delete Error"),
                body: _t("You cannot delete a section with orders still in draft for this section."),
            });
        }
        // Value of an object can change inside async function call.
        //   Which means that in this code block, the value of `state.selectedSectionId`
        //   before the await call can be different after the finishing the await call.
        // Since we wanted to disable the selected section after deletion, we should be
        //   setting the selectedSectionId to null. However, we only do this if nothing
        //   else is selected during the rpc call.
        const equalsCheck = (a, b) => {
            return JSON.stringify(a) === JSON.stringify(b);
        };
        if (equalsCheck(this.state.selectedSectionIds, originalSelectedSectionIds)) {
            this.state.selectedSectionIds = [];
        }
        this.pos.TICKET_SCREEN_STATE.syncedOrders.cache = {};
    }
}

registry.category("pos_screens").add("FloorScreen", FloorScreen);
