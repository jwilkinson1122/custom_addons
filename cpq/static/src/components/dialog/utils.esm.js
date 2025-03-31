/** @odoo-module */

export async function nextTick() {
    await Promise.resolve();                 // microtask
    await new Promise(r => setTimeout(r));   // full task (flushes Owl reactivity too)
}

 

