/** @odoo-module **/

import KanbanController from "web.KanbanController"; 
import DataExport from "web.DataExport";
import dialogs from "web.view_dialogs";
import { qweb } from "web.core"

const ProductKanbanController = KanbanController.extend({
    events: _.extend({}, KanbanController.prototype.events, {
        "change #prodsort": "_applyProductSorting",
        "click .prodreverse_sort": "_applyReverseProdSorting",
        "click .prodselect_all": "addAll2SelectedProducts",
        "click .clear_categories": "_clearCategroies",
        "click .clear_attributes": "_clearAttributes",
        "click .clear_eshop_categories": "_clearEshopCategories",
        "click .clear_selected_products": "clearAllSelectedProducts",
        "click .podiatry_management_product_selected_row": "_removeProductSelected",
        "click .mass_action_button": "_proceedMassAction",
        "click .mass_action_export": "_massActionExport",
    }),
    jsLibs: [
        '/podiatry_management/static/lib/jstree/jstree.js',
    ],
    cssLibs: [
        '/podiatry_management/static/lib/jstree/themes/default/style.css',
    ],
    custom_events: _.extend({}, KanbanController.prototype.custom_events, {
        select_record: '_productSelected',
    }),
    /*
     * Re-write to declare controller settings
    */ 
    init: function () {
        this._super.apply(this, arguments);
        this.nonavigation_update = false;
        this.selectedRecords = [];
        this.navigationExist = false;
    },
    /*
     * Re-write to add proper kanban classes
    */ 
    start: function () {
        this.$('.o_content').addClass('podiatry_management_products prm_d_flex');
        return this._super.apply(this, arguments);
    },
    /*
     *  Re-write to render left navigation panel
    */ 
    _update: function () {
        var self = this;
        var def = $.Deferred();
        this._super.apply(this, arguments).then(function (res) {
            var state = self.model.get(self.handle);
            if (self.navigationExist) {
                def.resolve(res);
            }
            else {
                self._renderNavigationPanel().then(function () {
                    def.resolve(res);
                });
            };
            self.renderer.updateSelection(self.selectedRecords);
        });
        return def
    },
    /*
     * Re-write to avoid rerendering left navigation panel
    */ 
    update: function (params, options) {
        var domain = params.domain || []
        this.nonavigation_update = true;
        params.productSystemDomain = this._renderProducts();
        return this._super(params, options);
    },
    /*
     * Re-write to force reload
    */ 
    _reloadAfterButtonClick: function (kanbanRecord, params) {
        var self = this;
        $.when(this._super.apply(this, arguments)).then(function () {
            self.reload();
        });
    },
    /*
     * The method to re-order products based on selected key
    */ 
    _applyProductSorting: function(event, passed) {
        event.stopPropagation();
        var self = this;
        var sortKey = event.currentTarget.value;
        var data = this.model.get(this.handle);
        var list = this.model.localData[data.id];
        var asc = false;
        if (passed && passed.reverse) {
            if (list.orderedBy.length != 0 && list.orderedBy[0].name == sortKey) {
                asc = list.orderedBy[0].asc;
            }
            else {
                asc = true;
            };
        };
        // To hack default 'desc' instead of 'asc'
        list.orderedBy = [];
        list.orderedBy.push({name: sortKey, asc: asc});
        this.model.setSort(data.id, sortKey).then(function () {
            self.reload({});
        });
    },
    /*
     *  The method to reverse the sorting
    */ 
    _applyReverseProdSorting: function(event) {
        event.stopPropagation();
        this.$("#prodsort").trigger("change", {"reverse": true});
    },
    /*
     * The method to prepare jstree of categories for a current user
    */ 
    _renderCategories: function () {
        var self = this;
        self.$('#categories').jstree('destroy');
        var defer = $.Deferred();
        self._rpc({
            model: "product.category",
            method: 'return_categories_hierarchy',
            args: [],
        }).then(function (availableCategories) {
            var jsTreeOptions = {
                'core' : {
                    'themes': {'icons': false},
                    'check_callback' : true,
                    'data': availableCategories,
                    "multiple" : true,
                },
                "plugins" : [
                    "checkbox",
                    "state",
                    "search",
                ],
                "state" : { "key" : "categories" },
                "checkbox" : {
                    "three_state" : false,
                    "cascade": "down",
                    "tie_selection" : false,
                },
                "contextmenu": {
                    "select_node": false,
                },
            }

            var ref = self.$('#categories').jstree(jsTreeOptions);
            var jsTreeAnchor = self.$('#categories').jstree(true);
            self.$('#categories').on("state_ready.jstree", self, function (event, data) {
                // We register 'checks' only after restoring the tree to avoid multiple checked events
                self.$('#categories').on("check_node.jstree uncheck_node.jstree", self, function (event, data) {
                    self.reload();
                });
                self.$('#categories').on("open_node.jstree", self, function (event, data) {
                    self._highlightParent(jsTreeAnchor, jsTreeAnchor.get_checked(), "#categories");
                });
            });
            defer.resolve();
        });
        return defer
    },
    /*
     * The method to prepare jstree of public categories for a current user
    */ 
    _renderEshopCategories: function () {
        var self = this;
        self.$('#eshop_categories').jstree('destroy');
        var defer = $.Deferred();
        self._rpc({
            model: "product.template",
            method: 'return_eshop_categories_hierarchy',
            args: [],
        }).then(function (availableCategories) {
            if (availableCategories.length > 0) {
                var jsTreeOptions = {
                    'core' : {
                        'themes': {'icons': false},
                        'check_callback' : true,
                        'data': availableCategories,
                        "multiple" : true,
                    },
                    "plugins" : [
                        "checkbox",
                        "state",
                        "search",
                    ],
                    "state" : { "key" : "eshop_categories" },
                    "checkbox" : {
                        "three_state" : false,
                        "cascade": "down",
                        "tie_selection" : false,
                    },
                    "contextmenu": {
                        "select_node": false,
                    },
                }
                var ref = self.$('#eshop_categories').jstree(jsTreeOptions);
                var jsTreeAnchor = self.$('#eshop_categories').jstree(true);
                self.$('#eshop_categories').on("state_ready.jstree", self, function (event, data) {
                    // We register 'checks' only after restoring the tree to avoid multiple checked events
                    self.$('#eshop_categories').on("check_node.jstree uncheck_node.jstree", self, function (event, data) {
                        self.reload();
                    })
                    self.$('#eshop_categories').on("open_node.jstree", self, function (event, data) {
                        self._highlightParent(jsTreeAnchor, jsTreeAnchor.get_checked(), "#eshop_categories");
                    })
                });
            }
            else {
                var toHideCategories = self.$('.podiatry_management_content').find(".not_shown_eshop_categories");
                toHideCategories.addClass("podiatry_management_hidden");
            }
            defer.resolve();
        });
        return defer
    },
    /*
     * The method to prepare jstree of attributes for a current user
    */ 
    _renderAttributes: function () {
        var self = this;
        var defer = $.Deferred();
        self.$('#attributes').jstree('destroy');
        self._rpc({
            model: "product.attribute",
            method: 'return_attributes_and_values',
            args: [],
        }).then(function (availableAttributes) {
            if (availableAttributes.length > 0) {
                var jsTreeOptions = {
                    'core' : {
                        'themes': {'icons': false},
                        'check_callback' : true,
                        'data': availableAttributes,
                        "multiple" : true,
                    },
                    "plugins" : [
                        "checkbox",
                        "state",
                        "search",
                    ],
                    "state" : { "key" : "attributes" },
                    "checkbox" : {
                        "three_state" : false,
                        "cascade": "down",
                        "tie_selection" : false,
                    },
                    "contextmenu": {
                        "select_node": false,
                    },
                }
                var ref = self.$('#attributes').jstree(jsTreeOptions);
                var jsTreeAnchor = self.$('#attributes').jstree(true);
                self.$('#attributes').on("state_ready.jstree", self, function (event, data) {
                    self.reload({"domain": self.model.get(self.handle).domain});
                    // We register 'checks' only after restoring the tree to avoid multiple checked events
                    self.$('#attributes').on("check_node.jstree uncheck_node.jstree", self, function (event, data) {
                        self.reload();
                    })
                    self.$('#attributes').on("open_node.jstree", self, function (event, data) {
                        self._highlightParent(jsTreeAnchor, jsTreeAnchor.get_checked(), "#attributes");
                    })
                });
                defer.resolve();
            }
            else {
                self.reload({"domain": self.model.get(self.handle).domain}).then(function () {
                    defer.resolve();
                });
                var toHideAttributes = self.$('.podiatry_management_content').find(".not_shown_attributes");
                toHideAttributes.addClass("podiatry_management_hidden");
            };
            
        });
        return defer
    },
    /*
     * The method to render left navigation panel
    */ 
    _renderNavigationPanel: function () {
        var self = this;
        var scrollTop = self.$('.podiatry_management_navigation_panel').scrollTop();
        self.$('.podiatry_management_navigation_panel').remove();
        var navigationElements = {};
        var $navigationPanel = $(qweb.render('ProductNavigationPanel', navigationElements));
        self.$('.o_content').prepend($navigationPanel);
        var def = $.Deferred();

        self._renderCategories().then(function () {
            self._renderEshopCategories().then(function () {
                self._renderAttributes().then(function () {
                    def.resolve();
                });
            });
        });
        self.$('.podiatry_management_navigation_panel').scrollTop(scrollTop || 0);
        self.navigationExist = true;
        return def
    },
    /*
     * The method to render right navigation panel
    */ 
    _renderRightNavigationPanel: function () {
        var self = this;
        var scrollTop = self.$('.podiatry_management_right_navigation_panel').scrollTop();
        self.$('.podiatry_management_right_navigation_panel').remove();
        var selectedRecords = this.selectedRecords;
        if (selectedRecords.length) {
            self._rpc({
                model: "product.template",
                method: 'return_selected_products',
                args: [this.selectedRecords],
                context: {},
            }).then(function (products) {
                var $navigationPanel = $(qweb.render(
                    'ProductRightNavigationPanel', {
                        "products": products[0],
                        "count_products": products[0].length,
                        "mass_actions": products[1],
                        "export_conf": products[2],
                    })
                );
                self.$('.o_content').append($navigationPanel);
                self.$('.podiatry_management_right_navigation_panel').scrollTop(scrollTop || 0);
            });
        }
    },
    /*
    * The method to highlight not selected parent nodes that have selected children
    * That's triggered when a node is selected or opened. The reason for the latter is that not loaded nodes get
    * class from state while we do not want to always iterate over those
    */
    _highlightParent(jsTreeAnchor, checkedNodes, jsSelector) {
        $(jsSelector + "* .podiatry_management_selected_parent").removeClass("podiatry_management_selected_parent");
        var allParentNodes = [];
        _.each(checkedNodes, function (node) {
            const thisNodeParents = jsTreeAnchor.get_path(node, false, true);
            allParentNodes = allParentNodes.concat(thisNodeParents);
        });
        allParentNodes = [... new Set(allParentNodes)];
        _.each(allParentNodes, function(nodeID) {
            $(jsSelector + " * .jstree-node#" + nodeID).addClass("podiatry_management_selected_parent");
        });
    },
    /*
     * The method to prepare new filters and trigger products rerender
    */ 
    _renderProducts: function () {
        var self = this;
        var domain = [];
        var refS = self.$('#categories').jstree(true),
            checkedCategories = refS.get_checked(),
            checkedCategoriesIDS = checkedCategories.map(function(item) {
                return parseInt(item, 10);
            });
        if (checkedCategoriesIDS.length != 0) {
            domain.push(['categ_id', 'in', checkedCategoriesIDS]);
        };
        this._highlightParent(refS, checkedCategories, '#categories');
        var refE = self.$('#eshop_categories').jstree(true);
        if (refE) {
            var checkedEshopCategs = refE.get_checked();
            var eCategsLength = checkedEshopCategs.length;
            if (eCategsLength != 0) {
                var iterator = 0;
                while (iterator != eCategsLength-1) {
                    domain.push('|');
                    iterator ++;
                }
                _.each(checkedEshopCategs, function (eCategory) {
                    if (eCategory.length) {
                        domain.push(['public_categ_ids', 'in', parseInt(eCategory)]);
                    }
                });
            };
            this._highlightParent(refE, checkedEshopCategs, '#eshop_categories');
        };
        var refT = self.$('#attributes').jstree(true);
        if (refT) {
            var allAttrs = refT.get_checked(true),
                checkedAttributes= [];
            _.each(allAttrs, function (attr_to_check) {
                if (attr_to_check.parent != "#") {
                    var already = false;
                    _.each(checkedAttributes, function (existing_attr) {
                        if (existing_attr.id === attr_to_check.parent) {
                            existing_attr.values.push(parseInt(attr_to_check.id));
                            already = true;
                        };
                    });
                    if (!already) {
                        checkedAttributes.push({
                            "id": attr_to_check.parent,
                            "values": [parseInt(attr_to_check.id)],
                        });
                    };
                };
            });
            _.each(checkedAttributes, function (attr) {
                var or_len = attr.values.length;
                var iterator = 0;
                while (iterator != or_len-1) {
                    domain.push('|');
                    iterator ++;
                }
                _.each(attr.values, function (val) {
                    domain.push(['attribute_value_to_search_ids', 'in', val]);
                });
            });
            this._highlightParent(refT, allAttrs, '#attributes');
        };
        return domain;
    },
    /*
     * The method to uncheck all categories
    */ 
    _clearCategroies: function(event) {
        var self = this;
        var ref = self.$('#categories').jstree(true);
        ref.uncheck_all();
        ref.save_state()
        self.reload();
    },
    /*
     * The method to uncheck all attributes
    */ 
    _clearAttributes: function(event) {
        var self = this;
        var ref = self.$('#attributes').jstree(true);
        ref.uncheck_all();
        ref.save_state()
        self.reload();
    },
    /*
     * The method to uncheck all public categroies
    */ 
    _clearEshopCategories: function(event) {
        var self = this;
        var ref = self.$('#eshop_categories').jstree(true);
        ref.uncheck_all();
        ref.save_state()
        self.reload();
    },
    /*
     * The method to add product for selection
    */ 
    _productSelected: function(event) {
        event.stopPropagation();
        var eventData = event.data;
        var addToSelection = eventData.selected;
        if (addToSelection) {
            this.selectedRecords.push(eventData.resID);
        }
        else {
            this.selectedRecords = _.without(this.selectedRecords, eventData.resID);
        };
        this._renderRightNavigationPanel();
    },
    /*
     * The method to add all products found to the selection
    */ 
    addAll2SelectedProducts: function(event) {
        // 
        event.stopPropagation();
        var self = this;
        var alreadySelected = this.selectedRecords;
        var data = this.model.get(this.handle);
        var list = this.model.localData[data.id];
        // We can't use res_ids since it only the first page --> so we rpc search
        this._rpc({
            model: "product.template",
            method: 'rerurn_all_pages_ids',
            args: [alreadySelected, list.domain],
            context: {},
        }).then(function (resIDS) {
            self.selectedRecords = resIDS;
            self.renderer.updateSelection(resIDS);
            self._renderRightNavigationPanel();
        });
    },
    /*
     * The method to remove all products from selection
    */ 
    clearAllSelectedProducts: function(event) {
        event.stopPropagation();
        this.selectedRecords = [];
        this.renderer.updateSelection(this.selectedRecords);
        this._renderRightNavigationPanel();
    },
    /*
     * The method to remove this article from selected
    */ 
    _removeProductSelected: function(event) {
        event.stopPropagation();
        var resID = parseInt(event.currentTarget.id);
        this.selectedRecords = _.without(this.selectedRecords, resID);
        this.renderer.updateSelection(this.selectedRecords);
        this._renderRightNavigationPanel();
    },
    /*
     * The method to apply related Odoo server action
    */ 
    _proceedMassAction: function(event) {
        event.stopPropagation();
        var self = this;
        var actionID = parseInt(event.currentTarget.id);
        this._rpc({
            model: "product.template",
            method: "proceed_mass_action",
            args: [this.selectedRecords, actionID],
            context: {},
        }).then(function (res) {
            if (!res) {
                self.reload();
            }
            else if (res.view_id) {
                var onSaved = function(record) {
                    self.reload();
                };
                new dialogs.FormViewDialog(self, {
                    res_model: res.res_model,
                    context: {'default_products': self.selectedRecords.join()},
                    title: res.display_name,
                    view_id: res.view_id,
                    readonly: false,
                    shouldSaveLocally: false,
                    on_saved: onSaved,
                }).open();
            }
            else if (res.action) {
                self.do_action(
                    res.action, 
                    {on_close: () => self.reload()}
                );
            }
            else {
                self.reload();
            }
        });
    },
    /*
     * The method to handle click to export records
    */ 
    _massActionExport: function(event) {
        var record = this.model.get(this.handle);
        var ExportFields = ["sequence", "default_code", "name", "list_price", "standard_price", "categ_id", "type",]
        new DataExport(this, record, ExportFields, this.renderer.state.groupedBy, this.getActiveDomain(), this.selectedRecords).open();
    },
    /*
     * The method is required to construct export popup
    */ 
    getActiveDomain: function () {
        return [["id", "in", this.selectedRecords]];
    },
});

export default ProductKanbanController;
