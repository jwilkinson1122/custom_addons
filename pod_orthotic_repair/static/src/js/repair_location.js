odoo.define('pod_orthotic_repair.custom_script', function (require) {"use strict";
     var ajax = require('web.ajax');
     $(document).ready(function () {
         $("#country_id").on("change", function () {
         console.log('print...............')
             var text = "<option value='' selected='selected'>Select State</option>"
             var countryId = $(this).val();
             ajax.jsonRpc("/get_country_wise_state", 'call', {
                 country_id: countryId
             }).then(function (country_wise_state) {
                 if (country_wise_state) {
                 for (var key in country_wise_state) {
                 text = text + '<option value="' + key + '">' + country_wise_state[key] + '</option>'
                 }
                 $('#state_id').empty().append(text);
                 }
             });
        });
     });
});