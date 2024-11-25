odoo.define("affiliate.update_kanban", function (require) {
  "use strict";

  var KanbanRecord = require("web.KanbanRecord");

  KanbanRecord.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     */
    _openRecord: function () {
      if (
        this.modelName === "affiliate" &&
        this.$(".o_project_kanban_boxes a").length
      ) {
        this.$(".o_project_kanban_boxes a").first().click();
      } else {
        this._super.apply(this, arguments);
      }
    },
  });
});
