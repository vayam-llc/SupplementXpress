odoo.define('pos_partner.models', function (require) {
"use strict";


var models = require('point_of_sale.models');
var pos_db = require('point_of_sale.DB');
var chrome = require('point_of_sale.chrome');


var _super_posmodel = models.PosModel.prototype;

    //Appending the new customer type model to pos models
    models.load_models([{
        model: 'customer.type',
        condition: function(self){ return true; },
        fields: ['name', 'description'],
        domain: null,
        loaded: function(self, partner_customer_type) {
            self.partner_customer_type = partner_customer_type;
            self.company.customer_type = null;
            for (var i = 0; i < partner_customer_type.length; i++) {
                    self.company.customer_type = partner_customer_type[i];

            }
        },}], { 'after': 'product.uom' });


    //Pushed customer type field to pos

    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function(model){ return model.model == 'res.partner'; });
            partner_model.fields.push('customer_type');
            return _super_posmodel.initialize.call(this, session, attributes);
        },
    });


});



