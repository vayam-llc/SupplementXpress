odoo.define('multi_price.models', function (require) {
"use strict";


var models = require('point_of_sale.models');
var pos_db = require('point_of_sale.DB')

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


});




});