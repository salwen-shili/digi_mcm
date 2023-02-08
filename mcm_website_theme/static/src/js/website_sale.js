odoo.define('mcm_website_theme.mcm_website_sale', function (require) {
  'use strict';

  var VariantMixin = require('sale.VariantMixin');
  var publicWidget = require('web.public.widget');
  var ajax = require('web.ajax');
  var core = require('web.core');
  var session = require('web.session');
  var rpc = require('web.rpc');
  var QWeb = core.qweb;

  //if user has comeback to the page after selecting cpf the input checkbox will be stuck on
  // cpf and the btn will show Je paye maintenant ! so we force credit card payment is checked as default
  // document.getElementById('stripe_pm').checked = true;

  publicWidget.registry.WebsiteSale.include({
    events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events, {
      // 'click #checkbox_instalment': 'verify_check',
      // "click #checkbox_conditions": "verify_conditions",
      'click #checkbox_failures': 'verify_failures',
      'click #checkbox_accompagnement': 'verify_accompagnement',
      // 'click #cpf_pm': 'verify_cpf',
      // 'click #stripe_pm': 'verify_cartebleu',
      'click #promo_code': 'show_coupon',
      //       'click #pm_shop_check': 'verify_pm',
      //       'click #pm_shop_checkout': 'verify_pm',
      //       'click #pm_shop': 'verify_pm',
    }),
    show_coupon: function (ev) {
      var self = this;
      if (document.getElementById('promo_input')) {
        document.getElementById('promo_input').style.display = 'inline';
      }
    },
    // verify_check: function (ev) {
    //   var self = this;
    //   var instalment = false;
    //   if (document.getElementById('checkbox_instalment').checked == true) {
    //     instalment = true;
    //     document.getElementById('order_amount_to_pay').style.visibility =
    //       'visible';
    //     if (document.getElementById('order_amount_to_pay_amount')) {
    //       document.getElementById(
    //         'order_amount_to_pay_amount'
    //       ).style.visibility = 'visible';
    //     }
    //     if (document.getElementById('order_instalment_number')) {
    //       document.getElementById('order_instalment_number').style.visibility =
    //         'visible';
    //     }
    //     if (document.getElementById('order_instalment_number_order')) {
    //       document.getElementById(
    //         'order_instalment_number_order'
    //       ).style.visibility = 'visible';
    //     }
    //   } else {
    //     instalment = false;
    //     document.getElementById('order_amount_to_pay').style.visibility =
    //       'hidden';
    //     if (document.getElementById('order_amount_to_pay_amount')) {
    //       document.getElementById(
    //         'order_amount_to_pay_amount'
    //       ).style.visibility = 'hidden';
    //     }
    //     if (document.getElementById('order_instalment_number')) {
    //       document.getElementById('order_instalment_number').style.visibility =
    //         'hidden';
    //     }
    //     if (document.getElementById('order_instalment_number_order')) {
    //       document.getElementById(
    //         'order_instalment_number_order'
    //       ).style.visibility = 'hidden';
    //     }
    //   }

    //   this._rpc({
    //     route: '/shop/payment/update_amount',
    //     params: {
    //       instalment: instalment,
    //     },
    //   }).then(function () {
    //     return true;
    //   });
    // },

    verify_pm: function (ev) {
      stripe_pm = document.getElementById('stripe_pm');
      if (stripe_pm) {
        if (stripe_pm.checked == true) {
          document.getElementById().href = '/shop/checkout?express=1';
          document.getElementById('pm_shop_check').href = '/shop/checkout?express=1';
          document.getElementById('pm_shop_checkout').href = '/shop/checkout?express=1';
          document.getElementById('pm_shop_checkout2').href = '/shop/checkout?express=1';
        } else {
          document.getElementById('pm_shop_check').href = '/new/ticket';
          document.getElementById('pm_shop_checkout').href = '/new/ticket';
          document.getElementById('pm_shop_checkout2').href = '/new/ticket';
        }
      }
    },
    // verify_conditions: function (ev) {
    //   console.log("input mcm change conditions ");
    //   var self = this;
    //   var condition = false;
    //   var conditions = document.getElementById("checkbox_conditions");
    //   if (document.getElementById("checkbox_conditions")) {
    //     if (document.getElementById("checkbox_conditions").checked == true) {
    //       var error = document.getElementById("error_conditions");
    //       if (error) {
    //         error.style.display = "none";
    //       }
    //       condition = true;
    //     } else {
    //       var error = document.getElementById("error_conditions");
    //       if (error) {
    //         error.style.display = "inline-block";
    //       }
    //       condition = false;
    //     }
    //   }
    //   this._rpc({
    //     route: "/shop/payment/update_condition",
    //     params: {
    //       condition: condition,
    //     },
    //   }).then(function () {
    //     return true;
    //   });
    // },
    verify_failures: function (ev) {
      var self = this;
      var failures = false;
      if (document.getElementById('checkbox_failures')) {
        if (document.getElementById('checkbox_failures').checked == true) {
          failures = true;
        } else {
          failures = false;
        }
      }
      this._rpc({
        route: '/shop/payment/update_failures',
        params: {
          failures: failures,
        },
      }).then(function () {
        return true;
      });
    },
    verify_accompagnement: function (ev) {
      var self = this;
      var accompagnement = false;
      if (document.getElementById('checkbox_accompagnement')) {
        if (document.getElementById('checkbox_accompagnement').checked == true) {
          accompagnement = true;
        } else {
          accompagnement = false;
        }
      }
      this._rpc({
        route: '/shop/payment/update_accompagnement',
        params: {
          accompagnement: accompagnement,
        },
      }).then(function () {
        return true;
      });
    },
  });

  publicWidget.registry.WebsiteSaleRegionDate = publicWidget.Widget.extend(VariantMixin, {
    selector: '#region_date_examen',
    events: _.extend({}, VariantMixin.events || {}, {
      'change select[name="region_examen"]': 'verify_centre',
      'change select[name="date_examen"]': 'verify_date_exam',
      //        'change input[id="checkbox_conditions"]': 'verify_conditions',
    }),
    verify_date_exam: function (ev) {
      var self = this;
      var center = false;
      var exam_date = document.getElementById('options-date');
      var center = document.getElementById('region_examen').value;
      var exam_date_id = false;

      if (exam_date) {
        var exam = document.getElementById('options-date').value;

        if (exam == 'all') {
          var error = document.getElementById('error_exam_date');
          if (error && exam_date.style.display == 'inline-block') {
            error.style.display = 'inline-block';
          }
        } else {
          var error = document.getElementById('error_exam_date');
          if (error) {
            error.style.display = 'none';
          }
        }
      }

      if (exam_date) {
        var exam_date_id = exam_date.options[exam_date.selectedIndex].id;
      }
      if (center && exam_date) {
        if (center == 'all' || exam_date.value == 'all') {
          var pm_button = document.getElementById('pm_shop_check');
          var pm_button_checkout = document.getElementById('pm_shop_checkout');
        }
      }
      this._rpc({
        route: '/shop/cart/update_exam_date_mcm',
        params: {
          exam_date_id: exam_date_id,
        },
      }).then(function (responseData) {
        if (responseData.hasOwnProperty("result")){
          if (responseData.result.hasOwnProperty("url_cpf")){
            urlCpf = responseData.result.url_cpf ?? false;
          }
          console.log("Url cpf: ", urlCpf)
          
        }

        return true;
      });
    },
  

    verify_centre: function (ev) {
      
      var datenb = 0;
      var self = this;
      var center = false;

      var center_exam = document.getElementById('region_examen');
      if (center_exam) {
        var center = document.getElementById('region_examen').value;

        var id = center_exam.options[center_exam.selectedIndex].id;
      }
      if (center_exam) {
        if (center_exam.value != 'all') {
          var t_modules = document.getElementById('exam_date');
          if (t_modules) {
            t_modules.style.display = 'inline-block';
          } else {
            t_modules.style.display = 'none';
          }
        }
      }

      

      //Filter departement by region
      var departementOptions = '';
      if ($('#departement_examen_data option')){
        $('#departement_examen_data option').each(function () {
          var departement =  this;
          
           
          
           if (departement.value.toUpperCase() === center.toUpperCase()) {
          
             var departementText = departement.text;
            
        
               departementOptions += `<option  value=${departement.value} id=${departement.id}>
                ${departementText}
               </option>`;
          
   
        
           }
           
         });

         var select_departement = `<select  name="departement_examen" id="departement_examen" class="form-control search-slt hide ">
         <option value="all" id="all" hidden="hidden" disabled="disabled" selected="true">
         Cliquez ici
                               </option>                  
         ${departementOptions}
                           </select>`;
         if (document.getElementById('departement_examen')){
           document.getElementById('departement_examen').innerHTML = select_departement;
         }
      }
   

      
      //end filter departement
      
      
      var dateOptions = '';
      $('#exam_date option').each(function () {
        var self = this;
        var select_option = $(this);

        var isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        var ios = false;
        if (isIOS) {
          ios = true;
        } else {
          ios = false;
        }
       
        if (self.value === center) {
          datenb++;
          var date = self.text;
          console.log('datenb', datenb);
          if (datenb < 3) {
            dateOptions += `<option style='text-transform: capitalize' value=${self.value} id=${self.id}>
             ${date}
            </option>`;
          }

          // document.getElementById("options-date").appendChild(dateOptions);
        }
        if (self.value == center || self.value == 'all') {
          if (ios == true) {
            select_option.prop('disabled', false);
            select_option.prop('display', 'none');
          } else {
            select_option.show();
          }
        } else {
          if (ios == true) {
            select_option.prop('disabled', true);
            select_option.prop('display', 'inline');
          } else {
            select_option.hide(); //
          }
        }
      });

      if (dateOptions) {
        var select = `<select name="date_examen" id="options-date" style="font-size: 15px; font-weight: 600;" class="form-control search-slt" onchange="onChangeCheckButton()" >
          <option value="all" id="all" hidden="hidden" disabled="disabled" selected="true">
          Cliquez ici 
                                </option>                  
          ${dateOptions}
                            </select>`;
        document.getElementById('select-date').innerHTML = select;
        document.getElementById('pm_shop_checkout').removeAttribute('disabled');
        document.getElementById('pm_shop_checkout2').removeAttribute('disabled');
      } else {
        document.getElementById('select-date').innerHTML =
          'Pas de date disponible pour le moment.';
        document.getElementById('pm_shop_checkout').setAttribute('disabled', 'disabled');
        document.getElementById('pm_shop_checkout2').setAttribute('disabled', 'disabled');
      }

      if (center_exam) {
        var center = document.getElementById('region_examen').value;
        if (center == 'all') {
          var error = document.getElementById('error_exam_center');
          if (error) {
            error.style.display = 'inline-block';
          }
        } else {
          var error = document.getElementById('error_exam_center');
          if (error) {
            error.style.display = 'none';
          }
        }
      }

      var exam_date = document.getElementById('exam_date');
      if (exam_date) {
        if (exam_date.value != 'all') {
          exam_date.value = 'all';
        }
      }
      if (center && exam_date) {
        if (center == 'all' || exam_date == 'all') {
          var pm_button = document.getElementById('pm_shop_check');
          var pm_button_checkout = document.getElementById('pm_shop_checkout');
        }
      }
      onChangeCheckButton();
      this._rpc({
        route: '/shop/cart/update_exam_center',
        params: {
          center: center,
        },
      }).then(function () {
        return true;
      });
    },
  });
});
//

 
