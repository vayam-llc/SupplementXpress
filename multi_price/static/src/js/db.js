odoo.define('multi_price.db', function (require) {
"use strict";

var PosDB = require('point_of_sale.DB');
var models = require('point_of_sale.models');
var chrome = require('point_of_sale.chrome');


PosDB.include({

_product_search_string: function(product){
        console.log("inherited");
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
//            if (product.secondary_price){
//                 self.pos.get_order().get_selected_orderline().set_unit_price(self.pos.get_order().get_selected_orderline().get_product().secondary_price);
//            }

        }
    },


});


});