/** @odoo-module */

import { getLimits, useMovable, constrain } from "@point_of_sale/app/utils/movable_hook";
import { onWillUnmount, useEffect, useRef, Component } from "@odoo/owl";
import { Section } from "@pos_shop/app/floor_screen/section";
import { usePos } from "@point_of_sale/app/store/pos_hook";

const MIN_TABLE_SIZE = 30; // px

export class EditSection extends Component {
    static template = "pos_shop.EditSection";
    static props = {
        onSaveSection: Function,
        limit: { type: Object, shape: { el: [HTMLElement, { value: null }] } },
        section: Section.props.section,
        selectedSections: Array,
    };

    setup() {
        this.pos = usePos();
        useEffect(this._setElementStyle.bind(this));
        this.root = useRef("root");
        this.handles = {
            "top left": ["minX", "minY"],
            "top right": ["maxX", "minY"],
            "bottom left": ["minX", "maxY"],
            "bottom right": ["maxX", "maxY"],
        };
        // make section draggable
        useMovable({
            ref: this.root,
            onMoveStart: () => this.onMoveStart(),
            onMove: (delta) => this.onMove(delta),
        });
        // make section resizable
        for (const [handle, toMove] of Object.entries(this.handles)) {
            useMovable({
                ref: useRef(handle),
                onMoveStart: () => this.onMoveStart(),
                onMove: (delta) => this.onResizeHandleMove(toMove, delta),
            });
        }
        onWillUnmount(() => this.props.onSaveSection(this.props.section));
    }

    onMoveStart() {
        if (this.pos.floorPlanStyle == "kanban") {
            return;
        }
        this.startSection = { ...this.props.section };
        this.selectedSectionsCopy = {};
        for (let i = 0; i < this.props.selectedSections.length; i++) {
            this.selectedSectionsCopy[i] = { ...this.props.selectedSections[i] };
        }
        // stop the next click event from the touch/click release from unselecting the section
        document.addEventListener("click", (ev) => ev.stopPropagation(), {
            capture: true,
            once: true,
        });
    }

    onMove({ dx, dy }) {
        if (this.pos.floorPlanStyle == "kanban") {
            return;
        }
        const { minX, minY, maxX, maxY } = getLimits(this.root.el, this.props.limit.el);

        for (const [index, section] of Object.entries(this.selectedSectionsCopy)) {
            const position_h = section.position_h;
            const position_v = section.position_v;
            this.props.selectedSections[index].position_h = constrain(position_h + dx, minX, maxX);
            this.props.selectedSections[index].position_v = constrain(position_v + dy, minY, maxY);
        }

        this._setElementStyle();
    }

    onResizeHandleMove([moveX, moveY], { dx, dy }) {
        if (this.pos.floorPlanStyle == "kanban") {
            return;
        }
        // Working with min/max x and y makes constraints much easier to apply uniformly
        const { width, height, position_h: minX, position_v: minY } = this.startSection;
        const newSection = { minX, minY, maxX: minX + width, maxY: minY + height };

        const limits = getLimits(this.root.el, this.props.limit.el);
        const { width: elWidth, height: elHeight } = this.root.el.getBoundingClientRect();
        const bounds = {
            maxX: [minX + MIN_TABLE_SIZE, limits.maxX + elWidth],
            minX: [limits.minX, newSection.maxX - MIN_TABLE_SIZE],
            maxY: [minY + MIN_TABLE_SIZE, limits.maxY + elHeight],
            minY: [limits.minY, newSection.maxY - MIN_TABLE_SIZE],
        };
        newSection[moveX] = constrain(newSection[moveX] + dx, ...bounds[moveX]);
        newSection[moveY] = constrain(newSection[moveY] + dy, ...bounds[moveY]);

        // Convert back to server format at the end
        this.props.section.position_h = newSection.minX;
        this.props.section.position_v = newSection.minY;
        this.props.section.width = newSection.maxX - newSection.minX;
        this.props.section.height = newSection.maxY - newSection.minY;
        this._setElementStyle();
    }
    /**
     * Offsets the resize handles from the edge of the section. For square sections,
     * the offset is half the width of the handle (we just want a quarter circle
     * to be visible), for round sections it's half the width plus the distance of
     * the middle of the rounded border's arc to the edge.
     *
     * @param {`${'top'|'bottom'} ${'left'|'right'}`} handleName the handle for
     *  which to compute the style
     * @returns {string} the value of the style attribute for the given handle
     */
    computeHandleStyle(handleName) {
        const section = this.props.section;
        // 24 is half the handle's width
        let offset = -24;
        if (section.shape === "round") {
            // min(width/2, height/2) is the real border radius
            // 0.2929 is (1 - cos(45°)) to get in the middle of the border's arc
            offset += Math.min(section.width / 2, section.height / 2) * 0.2929;
        }
        return handleName
            .split(" ")
            .map((dir) => `${dir}: ${offset}px;`)
            .join(" ");
    }

    _setElementStyle() {
        const section = this.props.section;
        if (this.pos.floorPlanStyle == "kanban") {
            const floor = section.floor;
            const index = floor.sections.indexOf(section);
            const minWidth = 100 + 20;
            const nbrHorizontal = Math.floor(window.innerWidth / minWidth);
            const widthSection = (window.innerWidth - nbrHorizontal * 10) / nbrHorizontal;
            const position_h =
                widthSection * (index % nbrHorizontal) + 5 + (index % nbrHorizontal) * 10;
            const position_v =
                (widthSection + 25) * Math.floor(index / nbrHorizontal) +
                10 +
                Math.floor(index / nbrHorizontal) * 10;

            Object.assign(this.root.el.style, {
                left: `${position_h}px`,
                top: `${position_v}px`,
                width: `${widthSection}px`,
                height: `${widthSection}px`,
                background: section.color || "rgb(53, 211, 116)",
                "line-height": `${widthSection}px`,
                "border-radius": section.shape === "round" ? "1000px" : "3px",
                "font-size": widthSection >= 150 ? "32px" : "16px",
                opacity: "0.7",
            });
            return;
        }
        Object.assign(this.root.el.style, {
            left: `${section.position_h}px`,
            top: `${section.position_v}px`,
            width: `${section.width}px`,
            height: `${section.height}px`,
            background: section.color || "rgb(53, 211, 116)",
            "line-height": `${section.height}px`,
            "border-radius": section.shape === "round" ? "1000px" : "3px",
            "font-size": section.height >= 150 && section.width >= 150 ? "32px" : "16px",
        });
    }
}
