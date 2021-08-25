odoo.define('crm_marketing_automation.action_call', function (require) {
'use strict';
/**
 * Button 'Supprimer duplication' is near create Button
**/
var core = require('web.core');
//var rpc = require('web.rpc');
var ListController = require('web.ListController');
ListController.include({
   renderButtons: function($node) {
   this._super.apply(this, arguments);
       if (this.$buttons) {
         this.$buttons.find('.oe_action_button').click(this.proxy('action_def'));
       }
    },
    //--------------------------------------------------------------------------
    // Define Handler for new Custom Button
    //--------------------------------------------------------------------------
    /**
     * @private
     * @param {MouseEvent} event
     */
    action_def: function (e) {
        var self = this;
        var active_id = this.model.get(this.handle).getContext()['active_ids'];
        var model_name = this.model.get(this.handle).getContext()['active_model'];
             this._rpc({
                    model:'crm.lead',
                    method:'crm_import_data',
                    args:[""],
                })
   },
});
});