odoo.define('multi_price.models', function (require) {
"use strict";


var models = require('point_of_sale.models');
var pos_db = require('point_of_sale.DB');
var chrome = require('point_of_sale.chrome');

var _super_posmodel = models.PosModel.prototype;
var orderlinemodel = models.Orderline.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function(model){ return model.model === 'product.product'; });
            partner_model.fields.push('secondary_barcode');
            partner_model.fields.push('secondary_uom_id');
            partner_model.fields.push('secondary_price');
            partner_model.fields.push('secondary');

            return _super_posmodel.initialize.call(this, session, attributes);
        },
    });

    models.Orderline = models.Orderline.extend({

    get_unit: function(){
        var unit_id;
        console.log("uom11111");
        console.log(this.get_unit_price());
        if (this.product.secondary_price == this.get_unit_price()){
            console.log("inside true");
            unit_id = this.product.secondary_uom_id;
        }
        else{
        console.log("false");
         unit_id = this.product.uom_id;
        }

        if(!unit_id){
            return undefined;
        }
        unit_id = unit_id[0];
        if(!this.pos){
            return undefined;
        }
        console.log(this.product.secondary_uom_id[0]);
        return this.pos.units_by_id[unit_id];
    },

    });


chrome.OrderSelectorWidget.include({
    renderElement: function(){
        var self = this;
        this._super();
        var categ = [];
        var unit = [];
        for (var i in self.pos.categories){
            categ.push(self.pos.categories[i].name);
        }
        for (var i in self.pos.units){
            unit.push(self.pos.units[i].name);
        }
        this.$('.add-product').click(function(event){
            console.log("Asdas");
            var product = self.pos.get_order().get_selected_orderline().get_product();
            if (product.secondary_price){
                 self.pos.get_order().get_selected_orderline().set_unit_price(self.pos.get_order().get_selected_orderline().get_product().secondary_price);
            }

        });
    },
});





});

