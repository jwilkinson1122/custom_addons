/** @odoo-module */

export function clickOk() {
    return [
        {
            content: `go back`,
            trigger: `.receipt-screen .button.next`,
        },
    ];
}

export function isShown() {
    return [
        {
            content: "Invoice screen is shown",
            trigger: '.receipt-screen h2:contains("Invoice Printing")',
            run: () => {},
        },
    ];
}
