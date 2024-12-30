/** @odoo-module **/
import {SectionAndNoteListRenderer } from "@account/components/section_and_note_fields_backend/section_and_note_fields_backend"
import { patch } from "@web/core/utils/patch";

patch(SectionAndNoteListRenderer.prototype,{
    /*** The purpose of this patch is to allow sections in the one2many list
      primarily used on Sales Orders, Purchase Order and Invoices*/
    setup(){
    /** This function help to access the subtotal field in order line*/
        super.setup();
        this['subtotal_titleField'] = "price_subtotal"
    },
    isSectionOrNote(record = null) {
        /*Function to calculate the subtotal in a section */
        if(this.record){
            if (this.record.data['display_type'] === 'line_section') {
                var sequence = this.record.data.sequence;
                var all_rows = this.list.records;
                var subtotal = 0.0;
                var self_found = false;
                for (var i = 0; i < all_rows.length; i++) {
                    var row = all_rows[i].data;
                    // If the current section's sequence matches, start calculating subtotal
                    if (row.sequence == sequence) {
                        self_found = true;
                        continue;
                    }
                    // Stop accumulating subtotal when another section is found
                    if (self_found) {
                        if (row.display_type === 'line_section' && row.sequence != sequence){
                            break;
                        }
                        // Ensure that we are only adding product lines (not sections or notes)
                        if (!['line_section', 'line_note'].includes(row.display_type)) {
                            subtotal += row.price_subtotal || 0; // Add only product subtotals
                        }
                    }
                }
                // Assign the calculated subtotal to the section's price_subtotal field
                this.record.data.price_subtotal = subtotal;
            }
        }
        record = record || this.record;
        return ['line_section', 'line_note'].includes(record.data.display_type);
    },
    getCellClass(column, record) {
        /*Help to hide the fields in order line except Description and Subtotal*/
        var classNames = super.getCellClass(column, record);
        if (this.isSectionOrNote(record) && column.widget !== "handle" && column.name !== this.titleField && column.name !== this.subtotal_titleField) {
            return `${classNames} o_hidden`;
        }
        if (column.name == 'price_subtotal' && classNames.includes("o_hidden")){
            classNames = classNames.replace("o_hidden", "").trim();
        }
        return classNames;
    },
    getColumns(record) {
        /*Check whether we select Line section or Line note and call
         the corresponding function*/
        const columns = this.columns;
        if (this.isSectionOrNote(record)) {
            if(record.data.display_type == 'line_note'){
                const columns = this.columns;
                return this.getSectionColumns(columns);
            }
            else{
                const columns = this.columns;
                return this.getSubtotalSectionColumns(columns);
            }
        }
        return columns;
    },
    getSubtotalSectionColumns(columns) {
        /* Ensure that the subtotal field is visible in the section rows */
        const sectionCols = columns.filter((col) => col.widget === "handle" || col.type === "field" && col.name === this.subtotal_titleField || col.type === "field" && col.name === this.titleField);
        return sectionCols.map((col) => {
            if (col.name === this.titleField) {
                return { ...col, colspan: columns.length - sectionCols.length + 1 };
            } else {
                return { ...col };
            }
        });
    }
});
