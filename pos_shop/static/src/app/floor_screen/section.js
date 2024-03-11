/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class Section extends Component {
    static template = "pos_shop.Section";
    static props = {
        onClick: Function,
        section: {
            type: Object,
            shape: {
                position_h: Number,
                position_v: Number,
                width: Number,
                height: Number,
                shape: String,
                color: [String, { value: false }],
                name: String,
                seats: Number,
                "*": true,
            },
        },
    };

    setup() {
        this.pos = usePos();
        this.state = useState({
            containerHeight: 0,
            containerWidth: 0,
        });
    }
    get fontSize() {
        const size = this.state.containerHeight / 3;
        return size > 20 ? 20 : size;
    }
    get badgeStyle() {
        if (this.props.section.shape !== "round") {
            return `top: -6px; right: -6px;`;
        }

        const sectionHeight = this.state.containerHeight;
        const sectionWidth = this.state.containerWidth;
        const radius = Math.min(sectionWidth, sectionHeight) / 2;

        let left = 0;
        let bottom = 0;

        if (sectionHeight > sectionWidth) {
            left = radius;
            bottom = radius + (sectionHeight - sectionWidth);
        } else {
            bottom = radius;
            left = radius + (sectionWidth - sectionHeight);
        }

        bottom += 0.7 * radius - 8;
        left += 0.7 * radius - 8;

        return `bottom: ${bottom}px; left: ${left}px;`;
    }
    computePosition(index, nbrHorizontal, widthSection) {
        const position_h = widthSection * (index % nbrHorizontal) + 5 + (index % nbrHorizontal) * 10;
        const position_v =
            widthSection * Math.floor(index / nbrHorizontal) +
            10 +
            Math.floor(index / nbrHorizontal) * 10;
        return { position_h, position_v };
    }
    get style() {
        const section = this.props.section;
        let style = "";
        let background = section.color ? section.color : "rgb(53, 211, 116)";
        let textColor = "white";

        if (!this.isOccupied()) {
            background = "#00000020";
            const rgb = section.floor.background_color
                .substring(4, section.floor.background_color.length - 1)
                .replace(/ /g, "")
                .split(",");
            textColor =
                (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255 > 0.5 ? "black" : "white";
        }

        style += `
            border: 3px solid ${section.color};
            border-radius: ${section.shape === "round" ? 1000 : 3}px;
            background: ${background};
            box-shadow: 0px 3px rgba(0,0,0,0.07);
            padding: ${section.shape === "round" ? "4px 10px" : "4px 8px"};
            color: ${textColor};`;

        if (this.pos.floorPlanStyle == "kanban") {
            const floor = section.floor;
            const index = floor.sections.indexOf(section);
            const minWidth = 120;
            const nbrHorizontal = Math.floor(window.innerWidth / minWidth);
            const widthSection = (window.innerWidth - nbrHorizontal * 10) / nbrHorizontal;
            const { position_h, position_v } = this.computePosition(
                index,
                nbrHorizontal,
                widthSection
            );

            this.state.containerHeight = widthSection;
            this.state.containerWidth = widthSection;

            style += `
                width: ${widthSection}px;
                height: ${widthSection}px;
                top: ${position_v}px;
                left: ${position_h}px;
            `;
        } else {
            this.state.containerHeight = section.height;
            this.state.containerWidth = section.width;

            style += `
                width: ${section.width}px;
                height: ${section.height}px;
                top: ${section.position_v}px;
                left: ${section.position_h}px;
            `;
        }

        style += `
            font-size: ${this.fontSize}px;
            line-height: ${this.fontSize}px;`;

        return style;
    }
    get fill() {
        const customerCount = this.pos.getCustomerCount(this.props.section.id);
        return Math.min(1, Math.max(0, customerCount / this.props.section.seats));
    }
    get orderCount() {
        const section = this.props.section;
        const unsynced_orders = this.pos.getSectionOrders(section.id).filter(
            (o) =>
                o.server_id === undefined &&
                (o.orderlines.length !== 0 || o.paymentlines.length !== 0) &&
                // do not count the orders that are already finalized
                !o.finalized
        );
        let result;
        if (section.changes_count > 0) {
            result = section.changes_count;
        } else if (section.skip_changes > 0) {
            result = section.skip_changes;
        } else {
            result = section.order_count + unsynced_orders.length;
        }
        return !Number.isNaN(result) ? result : 0;
    }
    get orderCountClass() {
        const notifications = this._getNotifications();
        const countClass = {
            "order-count": true,
            "notify-printing text-bg-danger": notifications.printing,
            "notify-skipped text-bg-info": notifications.skipped,
            "text-bg-dark": !notifications.printing && !notifications.skipped,
        };
        return countClass;
    }
    get customerCountDisplay() {
        const customerCount = this.pos.getCustomerCount(this.props.section.id);
        if (customerCount == 0) {
            return `${this.props.section.seats}`;
        } else {
            return `${customerCount}/${this.props.section.seats}`;
        }
    }
    _getNotifications() {
        const section = this.props.section;

        const hasChangesCount = section.changes_count;
        const hasSkippedCount = section.skip_changes;

        return hasChangesCount ? { printing: true } : hasSkippedCount ? { skipped: true } : {};
    }
    isOccupied() {
        return (
            this.pos.getCustomerCount(this.props.section.id) > 0 || this.props.section.order_count > 0
        );
    }
}
