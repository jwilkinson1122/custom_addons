odoo.define('pod_contacts.ListRenderer', function (require) {
    "use strict";
        var ajax = require('web.ajax');
        var ListRenderer = require('web.ListRenderer');
         var core = require('web.core');
        var _t = core._t;
    
    
        ListRenderer.include({
            _renderAppear: function (tag) {
                var $content = '<div class="o_display_form1"><span class="fa fa-sitemap"/></div>'
                return $('<' + tag + ' width="1" colspan="2">')
                    .addClass('hierarchy_contacts')
                    .append($content);
            },
    
            _renderAppear_blank: function (tag) {
                var $content = '<div class="contacts_hierarchy" ><span class="fa" id="black_fa"/></div>'
                return $('<' + tag + ' width="1" colspan="2">')
                    .addClass('hierarchy_contacts')
                    .append($content);
            },
            
            _renderHeader: function () {
                var th = this._super.apply(this, arguments);
                var self = this
                var tr = th[0].children[0]
                 if(self.hasSelectors) {
                    if(!self.isGrouped){
                        $(tr).prepend('<th width="1" colspan="2"></th>');	
                    }
                }
                return th  
            },
    
            _renderFooter: function () {
                var aggregates = {};
                _.each(this.columns, function (column) {
                    if ('aggregate' in column) {
                        aggregates[column.attrs.name] = column.aggregate;
                    }
                });
                var $cells = this._renderAggregateCells(aggregates);
                if (this.hasSelectors) {
                    $cells.unshift($('<td>'));
                    if(!this.isGrouped){
                        $cells.unshift($('<td>'));
                    }
                }
                return $('<tfoot>').append($('<tr>').append($cells));
            },
    
            _getNumberOfCols: function () {
                var self = this._super.apply(this, arguments);
                return self + 1
            },
    
            _renderRow: function (record) {
                var tr = this._super.apply(this, arguments);
                var self = this;
                if(self.hasSelectors){
                    if(!self.isGrouped ){
                        if(self.state.domain.length == 0 && self.state.model == 'res.partner'){
                            tr.prepend(self._renderAppear_blank('td', !record.res_id));
                            ajax.jsonRpc('/check/child', 'call',{'id':record.data.id}).then(function(val){
                                setTimeout(function(){
                                    if($('.breadcrumb-item').text() == 'Contacts Hierarchy'){
                                        if(val){
                                            tr.find('#black_fa').addClass('fa-sitemap');
                                            tr.addClass('parent_tr')
                                            tr.css({'background-color':'#e9ecef','font-weight':'bold'})
                                            tr.show();
                                        }
                                        else{
                                            tr.find('#black_fa').parent().removeClass('contacts_hierarchy');
                                            tr.addClass('child_tr')
                                            // tr.hide();
                                        }
                                    }
                                },100)
                            })
    
                        }else{
                            tr.prepend(this._renderAppear_blank('td', !record.res_id));
                        }
                    }
                }
                return tr;
            },
            
            _renderRows: function(){
                var $rows = this._super();
                var self = this
                 var datas = self.state.data
                if(self.state.model == 'res.partner' && self.state.domain.length == 0){
                     var parent_partner = []
                    var obj = this.state.data
                    for(var item in obj) {
                        if (obj[item].data.parent_id != false){
                            parent_partner.push(obj[item].id)
                        }
                    }
                    setTimeout(function(){
                        if($('.breadcrumb-item').text() == 'Contacts Hierarchy'){
                            var o_data_row = $('.o_content').find('.o_data_row')
                            for(var i in o_data_row){
                                if(o_data_row[i].dataset){
                                    $(o_data_row[i])[0].res_id = datas[i].res_id
                                }
                            }
                        }
                    },500);
                }
                return $rows
            },
    
            async _renderView() {
                var self = this._super.apply(this, arguments);
                var m_self = this
                setTimeout(function(){
                    if($('.breadcrumb-item').text() == 'Contacts Hierarchy' && m_self.viewType == 'list'){
                        $('.o_content').find('.o_data_row').hide();
                        $('.o_searchview').hide()
                        $('.o_search_options').hide()
                    }
                },100)
                 m_self._onClick_icon()
                 return self;
            },
    
            _onClick_icon: function () {
                var self = this;
                setTimeout(function(){
                    $('.contacts_hierarchy').click(function(ev){
                        ev.stopPropagation()
                        var tr = ev.currentTarget.offsetParent.parentElement
                        var o_data_row = $('.o_content').find('.o_data_row')
                        var id = false;
                        if($(tr)[0].res_id){
                            id = $(tr)[0].res_id;
                        }
                        else{
                            _.each(self.state.data, function (data) {
                               if(data.id == $(ev.currentTarget).parents('tr').data('id')){
                                    id = data.res_id;
                               }
                            });
                        }
                        ajax.jsonRpc('/customer/hierarchy', 'call',{'id':id}).then(function(val){
                            var current_child = []
                             for(var data in o_data_row){
                                if (jQuery.inArray(o_data_row[data].res_id, val) > -1){
                                    current_child.push(o_data_row[data])
                                }
                            }
                            if(!$(tr).hasClass('show')){
                                $('.child_tr').hide()
                                $(current_child).show()
                                 $(tr).addClass('show')
                            }
                            else{
                                $(tr).removeClass('show')
                                $(current_child).hide()
                            }
                            $(current_child).find('.fa-sitemap').remove()
                        })
                    })
                },1000)
            }
        });
        
    });