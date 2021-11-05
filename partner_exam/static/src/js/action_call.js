odoo.define('partner_exam.action_call', function (require) {
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
         this.$buttons.find('.oe_new_button').click(this.proxy('button_def'));
         this.$buttons.find('.oe_absent_button').click(this.proxy('absent_def'));
       }
    },
    //--------------------------------------------------------------------------
    // Define Handler for new Custom Button
    //--------------------------------------------------------------------------
    /**
     * @private
     * @param {MouseEvent} event
     */
    button_def: function (e) {
        var self = this;
        var active_id = this.model.get(this.handle).getContext()['active_ids'];
        var model_name = this.model.get(this.handle).getContext()['active_model'];
             this._rpc({
                    model:'info.examen',
                    method:'change_etat_wedof',
                    args:[""],
                })
   },
     absent_def: function (e) {
        var self = this;
        var active_id = this.model.get(this.handle).getContext()['active_ids'];
        var model_name = this.model.get(this.handle).getContext()['active_model'];
             this._rpc({
                    model:'info.examen',
                    method:'change_etat_wedof_absent',
                    args:[""],
                })
   },

});
});