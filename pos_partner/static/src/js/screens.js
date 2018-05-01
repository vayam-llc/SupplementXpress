odoo.define('pos_partner.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;

    screens.PaymentScreenWidget.include({
        validate_order: function(options) {
            if(this.pos.config.require_customer != 'no'
                    && !this.pos.get('selectedOrder').get_client()){
                this.gui.show_popup('error',{
                    'title': _t('An anonymous order cannot be confirmed'),
                    'body':  _t('Please select a customer for this order.'),
                });
                return;
            }
            return this._super(options);
        }
    });

    screens.ClientListScreenWidget.include({
        display_client_details: function(visibility,partner,clickpos){
                var self = this;
                var searchbox = this.$('.searchbox input');
                var contents = this.$('.client-details-contents');
                var parent   = this.$('.client-list').parent();
                var customertype = this.$('.client-customer_type');
                var scroll   = parent.scrollTop();
                var height   = contents.height();

                contents.off('click','.button.edit');
                contents.off('click','.button.save');
                contents.off('click','.button.undo');
                contents.on('click','.button.edit',function(){ self.edit_client_details(partner); });
                contents.on('click','.button.save',function(){ self.save_client_details(partner); });
                contents.on('click','.button.undo',function(){ self.undo_client_details(partner); });
                this.editing_client = false;
                this.uploaded_picture = null;

                if(visibility === 'show'){
                    contents.empty();
                    contents.append($(QWeb.render('ClientDetails',{widget:this,partner:partner})));

                    var new_height   = contents.height();
                    if(!this.details_visible){
                        // resize client list to take into account client details
                        parent.height('-=' + new_height);

                        if(clickpos < scroll + new_height + 20 ){
                            parent.scrollTop( clickpos - 20 );
                        }else{
                            parent.scrollTop(parent.scrollTop() + new_height);
                        }
                    }else{
                        parent.scrollTop(parent.scrollTop() - height + new_height);
                    }

                    this.details_visible = true;
                    this.toggle_save_button();
                } else if (visibility === 'edit') {
                    // Connect the keyboard to the edited field
                    if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                        contents.off('click', '.detail');
                        searchbox.off('click');
                        contents.on('click', '.detail', function(ev){
                            self.chrome.widget.keyboard.connect(ev.target);
                            self.chrome.widget.keyboard.show();
                        });
                        searchbox.on('click', function() {
                            self.chrome.widget.keyboard.connect($(this));
                        });
                    }
                    var test = self.pos.db._pricelist_filter(partner,this.pos) ;
                    this.editing_client = true;
                    contents.empty();
                    contents.append($(QWeb.render('ClientDetailsEdit',{widget:this,partner:partner})));
                    this.toggle_save_button();

                    // Browsers attempt to scroll invisible input elements
                    // into view (eg. when hidden behind keyboard). They don't
                    // seem to take into account that some elements are not
                    // scrollable.
                    contents.find('input').blur(function() {
                        setTimeout(function() {
                            self.$('.window').scrollTop(0);
                        }, 0);
                    });

                    contents.find('.image-uploader').on('change',function(event){
                        self.load_image_file(event.target.files[0],function(res){
                            if (res) {
                                contents.find('.client-picture img, .client-picture .fa').remove();
                                contents.find('.client-picture').append("<img src='"+res+"'>");
                                contents.find('.detail.picture').remove();
                                self.uploaded_picture = res;
                            }
                        });
                    });
                } else if (visibility === 'hide') {
                    contents.empty();
                    parent.height('100%');
                    if( height > scroll ){
                        contents.css({height:height+'px'});
                        contents.animate({height:0},400,function(){
                            contents.css({height:''});
                        });
                    }else{
                        parent.scrollTop( parent.scrollTop() - height);
                    }
                    this.details_visible = false;
                    this.toggle_save_button();
                }
            },
    });
 });