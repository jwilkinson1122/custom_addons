/* @odoo-module */

import { useService } from "@web/core/utils/hooks";
import { FileViewer as WebFileViewer } from "@web/core/file_viewer/file_viewer";
import { onWillUpdateProps } from "@odoo/owl";

export class FileViewer extends WebFileViewer {
    static template = "prescriptions.FileViewer";
    setup() {
        super.setup();
        /** @type {import("@prescriptions/core/prescription_service").PrescriptionService} */
        this.prescriptionService = useService("prescription.prescription");
        this.onSelectPrescription = this.prescriptionService.prescriptionList?.onSelectPrescription;
        onWillUpdateProps((nextProps) => {
            if (nextProps.startIndex !== this.state.index) {
                this.activateFile(nextProps.startIndex);
            }
        });
    }
    get hasSplitPdf() {
        if (this.prescriptionService.prescriptionList?.initialRecordSelectionLength === 1) {
            return this.prescriptionService.prescriptionList.selectedPrescription.attachment.isPdf;
        }
        return this.prescriptionService.prescriptionList?.prescriptions.every(
            (prescription) => prescription.attachment.isPdf
        );
    }
    get withDownload() {
        if (this.prescriptionService.prescriptionList?.initialRecordSelectionLength === 1) {
            return this.prescriptionService.prescriptionList.selectedPrescription.attachment.isUrlYoutube;
        }
        return this.prescriptionService.prescriptionList?.prescriptions.every(
            (prescription) => prescription.attachment.isUrlYoutube
        );
    }
    onClickPdfSplit() {
        this.close();
        if (this.prescriptionService.prescriptionList?.initialRecordSelectionLength === 1) {
            return this.prescriptionService.prescriptionList?.pdfManagerOpenCallback([
                this.prescriptionService.prescriptionList.selectedPrescription.record,
            ]);
        }
        return this.prescriptionService.prescriptionList?.pdfManagerOpenCallback(
            this.prescriptionService.prescriptionList.prescriptions.map((prescription) => prescription.record)
        );
    }
    close() {
        this.prescriptionService.prescriptionList?.onDeleteCallback();
        super.close();
    }
    next() {
        super.next();
        if (this.onSelectPrescription) {
            const prescriptionList = this.prescriptionService.prescriptionList;
            if (
                !prescriptionList ||
                !prescriptionList.selectedPrescription ||
                !prescriptionList.prescriptions ||
                !prescriptionList.prescriptions.length
            ) {
                return;
            }
            const index = prescriptionList.prescriptions.findIndex(
                (prescription) => prescription === prescriptionList.selectedPrescription
            );
            const nextIndex = index === prescriptionList.prescriptions.length - 1 ? 0 : index + 1;
            prescriptionList.selectedPrescription = prescriptionList.prescriptions[nextIndex];
            this.onSelectPrescription(prescriptionList.selectedPrescription.record);
        }
    }
    previous() {
        super.previous();
        if (this.onSelectPrescription) {
            const prescriptionList = this.prescriptionService.prescriptionList;
            if (
                !prescriptionList ||
                !prescriptionList.selectedPrescription ||
                !prescriptionList.prescriptions ||
                !prescriptionList.prescriptions.length
            ) {
                return;
            }
            const index = prescriptionList.prescriptions.findIndex(
                (doc) => doc === prescriptionList.selectedPrescription
            );
            // if we're on the first prescription, go "back" to the last one
            const previousIndex = index === 0 ? prescriptionList.prescriptions.length - 1 : index - 1;
            prescriptionList.selectedPrescription = prescriptionList.prescriptions[previousIndex];
            this.onSelectPrescription(prescriptionList.selectedPrescription.record);
        }
    }
}
