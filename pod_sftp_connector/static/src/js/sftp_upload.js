odoo.define("pod_sftp_connector.sftp_upload", function (require) {
  "use strict";

  var core = require("web.core");
  var rpc = require("web.rpc");

  var SftpUpload = core.Widget.extend({
    events: {
      "submit .oe_sftp_upload_form": "_onFormSubmit",
    },

    _onFormSubmit: function (ev) {
      ev.preventDefault();
      var self = this;
      var $form = $(ev.currentTarget);
      var fileInput = $form.find(".oe_sftp_file_input")[0];
      var file = fileInput.files[0];

      if (file) {
        var formData = new FormData();
        formData.append("file", file);
        formData.append("customer_id", self._getCustomerId()); // Get customer ID from context

        rpc
          .query({
            model: "res.partner",
            method: "upload_file_sftp",
            args: [formData],
          })
          .then(function (result) {
            // Handle successful upload (e.g., update file list)
            self.$(".oe_sftp_progress_bar").hide();
            // Update UI to reflect successful upload
          })
          .progress(function (progress) {
            // Update progress bar
            self
              .$(".oe_sftp_progress_fill")
              .css("width", progress.percent + "%");
            self.$(".oe_sftp_progress_text").text(progress.percent + "%");
          });
      }
    },

    _getCustomerId: function () {
      // Implement logic to retrieve the current customer ID from the context
      // For example, you could get it from a hidden field on the form
    },
  });

  core.action_registry.add("sftp_upload", SftpUpload);
});
