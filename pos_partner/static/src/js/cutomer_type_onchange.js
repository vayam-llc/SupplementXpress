odoo.define('pos_partner.customer_type_onchange', function (require) {
"use strict";

var models = require('point_of_sale.models');
var pos_db = require('point_of_sale.DB');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var _super_posmodel = models.PosModel.prototype;
var rpc = require('web.rpc');
var Widget = require('web.Widget');

pos_db.include({

_pricelist_filter:function(partner,order){
    $(document).on('click','.client-customer_type',function(){

                        var pricelistfield_element = document.getElementsByName("property_product_pricelist");
                        var sel_customer_type_id =  parseInt(event.target.value);
                        if (sel_customer_type_id){
                            if (_.findWhere(order.partner_customer_type, {'id': sel_customer_type_id})){
                                for (var i = 0; i < order.pricelists.length; i++) {
                                        if(order.pricelists[i].customer_type){
                                            if (sel_customer_type_id == order.pricelists[i].customer_type[0]){
                                                pricelistfield_element[0].value = order.pricelists[i].id;
                                            }
                                        }
                                    }


                            }
                        }

                    });
}

});

});