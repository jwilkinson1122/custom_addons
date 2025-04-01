/** @odoo-module */

import { onWillUnmount } from "@odoo/owl";

export function useDebouncedInput(delay = 300) {
    let timeout = null;

    onWillUnmount(() => {
        if (timeout) clearTimeout(timeout);
    });

    return (callback) => {
        return (ev) => {
            const value = ev?.target?.value ?? ev;

            if (timeout) clearTimeout(timeout);
            timeout = setTimeout(() => {
                callback(value);
            }, delay);
        };
    };
}


export async function nextTick() {
    await Promise.resolve();                 // microtask
    await new Promise(r => setTimeout(r));   // full task (flushes Owl reactivity too)
}

 

