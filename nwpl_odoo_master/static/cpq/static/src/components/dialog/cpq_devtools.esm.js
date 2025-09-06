/** @odoo-module **/

console.log("CPQ DevTools Loaded");

function waitForCPQDialog(timeout = 5000) {
    return new Promise((resolve, reject) => {
        const interval = 100;
        let waited = 0;

        const check = () => {
            if (window._cpqDevDialog) {
                resolve(window._cpqDevDialog);
            } else if (waited >= timeout) {
                reject("X Timeout: _cpqDevDialog not available");
            } else {
                waited += interval;
                setTimeout(check, interval);
            }
        };

        check();
    });
}

async function simulateCPQValidation(mockSelected) {
    const dlg = await waitForCPQDialog();
    console.log("Injecting test selection:", mockSelected);

    dlg.state.selected = mockSelected;

    const flattened = dlg._flattenCombination(dlg.state.selected);
    console.log("Flattened combination:", flattened);

    await dlg._validate();

    console.log("[OK] Valid?", dlg.state.valid);
    console.log("Errors:", dlg.state.errors);
}

async function simulateSplitLaterality(left, right) {
    const dlg = await waitForCPQDialog();
    dlg.state.split = true;
    dlg.state.laterality = "bilateral";
    dlg.state.selected = { left: left || {}, right: right || {} };
    console.log("Switched to split mode:", dlg.state.selected);
    await dlg._validate();
}

async function simulatePricePreview() {
    const dlg = await waitForCPQDialog();
    await dlg.updatePricePreview();
    console.log("Price Breakdown:", dlg.state.priceBreakdown);
}

async function simulateSave(confirm = false) {
    const dlg = await waitForCPQDialog();
    if (confirm) {
        window.confirm = () => true;
    }
    await dlg.onCreate();
    console.log("Save triggered.");
}

window._cpqDev = {
    waitForDialog: waitForCPQDialog,
    simulateValidation: simulateCPQValidation,
    simulateSplitLaterality,
    simulatePrice: simulatePricePreview,
    simulateSave,
};
