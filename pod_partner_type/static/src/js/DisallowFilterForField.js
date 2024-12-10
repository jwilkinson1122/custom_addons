/** @odoo-module **/

import { Layout } from "@web/search/layout";
import { useModelWithSampleData } from "@web/model/model";
import { standardViewProps } from "@web/views/standard_view_props";
import { useSetupView } from "@web/views/view_hook";
import { SearchBar } from "@web/search/search_bar/search_bar";
import { useSearchBarToggler } from "@web/search/search_bar/search_bar_toggler";
import { CogMenu } from "@web/search/cog_menu/cog_menu";
import { ModelFieldSelectorPopover } from "@web/core/model_field_selector/model_field_selector_popover";
import { DomainSelectorDialog } from "@web/core/domain_selector_dialog/domain_selector_dialog";
import { dialogService, DialogWrapper } from "@web/core/dialog/dialog_service";
import { patch } from '@web/core/utils/patch';
import { Component, useRef } from "@odoo/owl";
import { session } from '@web/session';
import { jsonrpc } from "@web/core/network/rpc_service";
import { useService } from '@web/core/utils/hooks';

patch(ModelFieldSelectorPopover.prototype, {
    /**
     * @override
     */

    filter(fieldDefs, path) {
        // fieldDefs?.expected_revenue?.searchable = false
        console.log(fieldDefs) // object that contains all field definitions of the respective model that are searchable
        console.log(path) // string that contains field name already in the input box
        const filteredKeys = Object.keys(fieldDefs).filter((k) =>
            this.props.filter(fieldDefs[k], path)
        );
        console.log(filteredKeys) // array of keys from field definition object
        console.log(Object.fromEntries(filteredKeys.map((k) => [k, fieldDefs[k]])))
        return Object.fromEntries(filteredKeys.map((k) => [k, fieldDefs[k]]));
    },

    searchFields(query) {
        let self = this;
        console.log(self.state.page.searchFields(query))
        this.state.page.searchFields(query);
    },

    // this.userService = useService("user");
    // const userGroups = await Promise.all(
    //     insertionGroups.map((group) => this.userService.hasGroup(group))
    // );
    
    // this.orm = useService('orm');

    // async fetchAttachments(limit, offset) {
    //     this.state.isFetchingAttachments = true;
    //     let attachments = [];
    //     try {
    //         attachments = await this.orm.call(
    //             'ir.attachment',
    //             'search_read',
    //             [],
    //             {
    //                 domain: this.attachmentsDomain,
    //                 fields: ['name', 'mimetype', 'description', 'checksum', 'url', 'type', 'res_id', 'res_model', 'public', 'access_token', 'image_src', 'image_width', 'image_height', 'original_id'],
    //                 order: 'id desc',
    //                 // Try to fetch first record of next page just to know whether there is a next page.
    //                 limit,
    //                 offset,
    //             }
    //         );
    //         attachments.forEach(attachment => attachment.mediaType = 'attachment');
    //     } catch (e) {
    //         // Reading attachments as a portal user is not permitted and will raise
    //         // an access error so we catch the error silently and don't return any
    //         // attachment so he can still use the wizard and upload an attachment
    //         if (e.exceptionName !== 'odoo.exceptions.AccessError') {
    //             throw e;
    //         }
    //     }
    //     this.state.canLoadMoreAttachments = attachments.length >= this.NUMBER_OF_ATTACHMENTS_TO_DISPLAY;
    //     this.state.isFetchingAttachments = false;
    //     return attachments;
    // }



    async selectField(field) {
        let self = this;
        console.log(self.state.page.path) // updated field name after it was selected
        console.log(field) // selected field name by the user i.e. expected_revenue. this can be utilized to enforce security rule
        const currentModel = this.props.resModel;
        await jsonrpc(`/web/dataset/call_kw/res.groups/search_read`, {
            model: "res.groups",
            method: "search_read",
            args: [[['name', '=', 'Disallowed User from Seeing Opportunity Revenues']]],
            // args: [{
                // 'auth_signup_uninvited': 'b2b',
                // 'show_line_subtotals_tax_selection': 'tax_included',
            // }],
            kwargs: {},
        }).then(function(returnedValueReturnedByCustomPythonMethod) {
           if((returnedValueReturnedByCustomPythonMethod[0].users).includes(session.uid) && currentModel == 'crm.lead' && field.name === "expected_revenue") {
                console.log(session)
               alert('You are not allowed to include this field in the filter')
           } else {
                if (field.type === "properties") {
                    return self.followRelation(field);
                }
                self.keepLast.add(Promise.resolve());
                self.state.page.selectedName = field.name;
                self.props.update(self.state.page.path);
                self.props.close();
        

           }
        });
        // DomainSelectorDialog.props.close();
        // console.log(DialogWrapper)
        // console.log(dialogService)

        // dialogService.remove();
    },

})
