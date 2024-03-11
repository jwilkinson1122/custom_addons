/** @odoo-module */

export function clickSection(name) {
    return [
        {
            content: `click section '${name}'`,
            trigger: `.floor-map .section .label:contains("${name}")`,
        },
    ];
}
export function clickFloor(name) {
    return [
        {
            content: `click '${name}' floor`,
            trigger: `.floor-selector .button-floor:contains("${name}")`,
        },
    ];
}
export function clickEdit() {
    return [
        {
            content: "Click Menu button",
            trigger: ".menu-button",
        },
        {
            content: `click edit button`,
            trigger: `.edit-button`,
        },
    ];
}
export function clickAddSection() {
    return [
        {
            content: "add section",
            trigger: `.edit-button i[aria-label=Add]`,
        },
    ];
}
export function clickDuplicate() {
    return [
        {
            content: "duplicate section",
            trigger: `.edit-button i[aria-label=Copy]`,
        },
    ];
}
export function clickRename() {
    return [
        {
            content: "rename section",
            trigger: `.edit-button i[aria-label=Rename]`,
        },
    ];
}
export function clickSeats() {
    return [
        {
            content: "change number of seats",
            trigger: `.edit-button i[aria-label=Seats]`,
        },
    ];
}
export function clickTrash() {
    return [
        {
            content: "trash section",
            trigger: `.edit-button.trash`,
        },
    ];
}
export function closeEdit() {
    return [
        {
            content: "Close edit mode",
            trigger: ".edit-button .close-edit-button",
        },
    ];
}
export function changeShapeTo(shape) {
    return [
        {
            content: `change shape to '${shape}'`,
            trigger: `.edit-button.button-option${shape === "round" ? ".round" : ".square"}`,
        },
    ];
}
export function ctrlClickSection(name) {
    return [
        {
            content: `ctrl click section '${name}'`,
            trigger: `.floor-map .section .label:contains("${name}")`,
            run: () => {
                $(`.floor-map .section .label:contains("${name}")`)[0].dispatchEvent(
                    new MouseEvent("click", { bubbles: true, ctrlKey: true })
                );
            },
        },
    ];
}
export function backToFloor() {
    return [
        {
            content: "back to floor",
            trigger: ".floor-button",
        },
    ];
}
export function selectedFloorIs(name) {
    return [
        {
            content: `selected floor is '${name}'`,
            trigger: `.floor-selector .button-floor.btn-primary:contains("${name}")`,
            run: () => {},
        },
    ];
}
export function selectedSectionIs(name) {
    return [
        {
            content: `selected section is '${name}'`,
            trigger: `.floor-map .section.selected .label:contains("${name}")`,
            run: () => {},
        },
    ];
}
export function hasSection(name) {
    return [
        {
            content: `selected floor has '${name}' section`,
            trigger: `.floor-map .section .label:contains("${name}")`,
            run: () => {},
        },
    ];
}
export function sectionSeatIs(section, val) {
    return [
        {
            content: `Unselect section`,
            trigger: `.floor-map`,
        },
        {
            content: `number of seats in section '${section}' is '${val}'`,
            trigger: `.floor-map .section .infos:has(.label:contains("${section}")) ~ .section-seats:contains("${val}")`,
            run: function () {},
        },
        {
            content: `click section '${section}'`,
            trigger: `.floor-map .section .label:contains("${section}")`,
        },
    ];
}
export function orderCountSyncedInSectionIs(section, count) {
    return [
        {
            trigger: `.floor-map .section .label:contains("${section}") ~ .order-count:contains("${count}")`,
            run: function () {},
        },
    ];
}
export function isShown() {
    return [
        {
            trigger: ".floor-map",
            run: function () {},
        },
    ];
}
export function sectionIsNotSelected(name) {
    return [
        {
            content: `section '${name}' is not selected`,
            trigger: `.floor-map .section:not(.selected) .label:contains("${name}")`,
            run: function () {},
        },
    ];
}
