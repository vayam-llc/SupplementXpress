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
            self.pos.get_order().get_selected_orderline().set_unit_price(self.pos.get_order().get_selected_orderline().get_product().secondary_price);
        });
    },
});

pos_db.PosDB = pos_db.PosDB.extend({

_product_search_string: function(product){
        var str = product.display_name;
        if (product.barcode) {
            str += '|' + product.barcode;
        }
        if (product.secondary_barcode) {
            str += '|' + product.secondary_barcode;
        }
        if (product.default_code) {
            str += '|' + product.default_code;
        }
        if (product.description) {
            str += '|' + product.description;
        }
        if (product.description_sale) {
            str += '|' + product.description_sale;
        }
        str  = product.id + ':' + str.replace(/:/g,'') + '\n';
        return str;
    },


      add_products: function(products){
        var stored_categories = this.product_by_category_id;

        if(!products instanceof Array){
            products = [products];
        }
        for(var i = 0, len = products.length; i < len; i++){
            var product = products[i];
            var search_string = this._product_search_string(product);
            var categ_id = product.pos_categ_id ? product.pos_categ_id[0] : this.root_category_id;
            product.product_tmpl_id = product.product_tmpl_id[0];
            if(!stored_categories[categ_id]){
                stored_categories[categ_id] = [];
            }
            stored_categories[categ_id].push(product.id);

            if(this.category_search_string[categ_id] === undefined){
                this.category_search_string[categ_id] = '';
            }
            this.category_search_string[categ_id] += search_string;

            var ancestors = this.get_category_ancestors_ids(categ_id) || [];

            for(var j = 0, jlen = ancestors.length; j < jlen; j++){
                var ancestor = ancestors[j];
                if(! stored_categories[ancestor]){
                    stored_categories[ancestor] = [];
                }
                stored_categories[ancestor].push(product.id);

                if( this.category_search_string[ancestor] === undefined){
                    this.category_search_string[ancestor] = '';
                }
                this.category_search_string[ancestor] += search_string;
            }
            this.product_by_id[product.id] = product;
            if(product.barcode){
                this.product_by_barcode[product.barcode] = product;
            }

            if(product.secondary_barcode){
                this.product_by_barcode[product.secondary_barcode] = product;
            }
        }
    },


});




});

