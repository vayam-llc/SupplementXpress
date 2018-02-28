odoo.define('pos_partner.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var _t = core._t;

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
 });