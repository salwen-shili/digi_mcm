odoo.define('mcm_website_theme.pack_homepage', function (require) {
  'use strict';

  var publicWidget = require('web.public.widget');

  publicWidget.registry.pack_homepage = publicWidget.Widget.extend({
    selector: '#sh_corpomate_theme_section_35',
    events: {
      'click #a_vtc': 'get_vtc_id',
      'click #a_taxi': 'get_taxi_id',
      'click #a_vmdtr': 'get_vmdtr_id',
    },
    get_vtc_id: function (ev) {
      var self = this;
      var product_id = false;
      var vtc = false;
      //console.log('teest');
      if (document.getElementById('vtc_product')) {
        //console.log('vtc_product');
        product_id = document.getElementById('vtc_product').value;
      }
      this._rpc({
        route: '/partner/update_choosed_product',
        params: {
          product_id: product_id,
        },
      }).then(function () {
        return true;
      });
    },
    get_taxi_id: function (ev) {
      var self = this;
      var product_id = false;
      var vtc = false;
      if (document.getElementById('taxi_product')) {
        product_id = document.getElementById('taxi_product').value;
      }
      this._rpc({
        route: '/partner/update_choosed_product',
        params: {
          product_id: product_id,
        },
      }).then(function () {
        return true;
      });
    },
    get_vmdtr_id: function (ev) {
      var self = this;
      var product_id = false;
      var vtc = false;
      if (document.getElementById('vmdtr_product')) {
        product_id = document.getElementById('vmdtr_product').value;
      }
      this._rpc({
        route: '/partner/update_choosed_product',
        params: {
          product_id: product_id,
        },
      }).then(function () {
        return true;
      });
    },
  });
});
