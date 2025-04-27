/** @odoo-module **/
import { Component, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { sendCpqQrScanEvent } from "./utils.esm";

export class CPQScanClient extends Component {
    setup() {
        this.notification = useService("notification");
        this.rpc = useService("rpc"); 
        onMounted(this._initScanner.bind(this));
    }

    async _initScanner() {
        const scanner = new Html5Qrcode("cpq-qr-scanner");
        const config = { fps: 10, qrbox: 250 };
        const onScanSuccess = async (decodedText) => {
            console.log("✅ QR Scanned:", decodedText);
            await this._handleScan(decodedText);
        };
        await scanner.start({ facingMode: "environment" }, config, onScanSuccess);
    }

    async _handleScan(payload) {
        try {
            const result = await sendCpqQrScanEvent(this.rpc, payload, "scan-in");
            if (result.success) {
                this.notification.add(`✅ Scan successful`, { type: "success" });
            } else {
                this.notification.add(`⚠️ Scan error: ${result.error || 'Unknown error'}`, { type: "danger" });
            }
        } catch (error) {
            this.notification.add("❌ Failed to process scan event.", { type: "danger" });
        }
    }
}

CPQScanClient.template = "cpq.CPQScanClient";
registry.category("actions").add("cpq.qr_scan_client", CPQScanClient);
