/** @odoo-module **/

import KanbanRecord from "web.KanbanRecord";

const ProductKanbanRecord = KanbanRecord.extend({
    events: _.extend({}, KanbanRecord.prototype.events, {
        'click .product_select': '_productSelect',
        'click .o_kanban_image': '_realOpenRecord',
    }),
    /*
     * The method to pass selection to the controller
    */ 
    _updateSelect: function (event, selected) {
        this.trigger_up('select_record', {
            originalEvent: event,
            resID: this.id,
            selected: selected,
        });
    },
    /*
     * The method to mark the product selected / disselected in the interface
    */ 
    _updateRecordView: function (select) {
        var kanbanCard = this.$el;
        var checkBox = this.$el.find(".product_select");
        if (select) {
            checkBox.removeClass("fa-square-o");
            checkBox.addClass("fa-check-square-o");
            kanbanCard.addClass("prodkanabanselected");
        }
        else {
            checkBox.removeClass("fa-check-square-o");
            checkBox.addClass("fa-square-o");
            kanbanCard.removeClass("prodkanabanselected");
        };
    },
    /*
     * The method to add to / remove from selection
    */ 
    _productSelect: function (event) {
        event.preventDefault();
        event.stopPropagation();
        var checkBox = this.$el.find(".product_select");
        if (checkBox.hasClass("fa-square-o")) {
            this._updateRecordView(true)
            this._updateSelect(event, true);
        }
        else {
            this._updateRecordView(false);
            this._updateSelect(event, false);
        }
    },
    /*
     * Re-write to make selection instead of opening a record
    */ 
    _openRecord: function (real) {
        if (!real) {
            this.$('.product_select').click();
        }
        else {
            this._super.apply(this, arguments);
        }
    },
    /*
     * Re-write to open product based on image click
    */     
    _realOpenRecord: function (event) {
        this._openRecord(true);
    },
});


export default ProductKanbanRecord;
