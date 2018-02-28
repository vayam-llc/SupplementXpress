odoo.define('multi_price.models', function (require) {
"use strict";


var models = require('point_of_sale.models');
var pos_db = require('point_of_sale.DB');
var chrome = require('point_of_sale.chrome');
var exports = {};

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

       scan_product: function(parsed_code){
        var selectedOrder = this.get_order();
        var product = this.db.get_product_by_barcode(parsed_code.base_code);


        if(!product){
            return false;
        }

        if(parsed_code.type === 'price'){
            selectedOrder.add_product(product, {price:parsed_code.value});
        }else if(parsed_code.type === 'weight'){
            selectedOrder.add_product(product, {quantity:parsed_code.value, merge:false});
        }else if(parsed_code.type === 'discount'){
            selectedOrder.add_product(product, {discount:parsed_code.value, merge:false});
        }
        else if(parsed_code.base_code === product.secondary_barcode){
            console.log("secondary"+product.secondary_price)
            selectedOrder.add_product(product, {secondary:product.secondary_price, merge:false});
        }
        else{
            selectedOrder.add_product(product);
        }
        return true;
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

models.Order = models.Order.extend({

        add_product: function(product, options){
        if(this._printed){
            this.destroy();
            return this.pos.get_order().add_product(product, options);
        }
        this.assert_editable();
        options = options || {};
        var attr = JSON.parse(JSON.stringify(product));
        attr.pos = this.pos;
        attr.order = this;
        var line = new models.Orderline({}, {pos: this.pos, order: this, product: product});

        if(options.secondary !== undefined){
            console.log("setting price"+options.secondary)
         line.set_unit_price(options.secondary)
        }

        if(options.quantity !== undefined){
            line.set_quantity(options.quantity);
        }

        if(options.price !== undefined){
            line.set_unit_price(options.price);
        }

        //To substract from the unit price the included taxes mapped by the fiscal position
        this.fix_tax_included_price(line);

        if(options.discount !== undefined){
            line.set_discount(options.discount);
        }

        if(options.extras !== undefined){
            for (var prop in options.extras) {
                line[prop] = options.extras[prop];
            }
        }

        var to_merge_orderline;
        for (var i = 0; i < this.orderlines.length; i++) {
            if(this.orderlines.at(i).can_be_merged_with(line) && options.merge !== false){
                to_merge_orderline = this.orderlines.at(i);
            }
        }
        if (to_merge_orderline){
            to_merge_orderline.merge(line);
        } else {
            this.orderlines.add(line);
        }
        this.select_orderline(this.get_last_orderline());

        if(line.has_product_lot){
            this.display_lot_popup();
        }
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

