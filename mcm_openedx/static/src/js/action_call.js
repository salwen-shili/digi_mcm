odoo.define('invoice.action_button', function (require) {
"use strict";
/**
 * Button 'Create' is replaced by Custom Button
**/

var core = require('web.core');
var ListController = require('web.ListController');
ListController.include({
   renderButtons: function($node) {
   this._super.apply(this, arguments);
       if (this.$buttons) {
         this.$buttons.find('.o_list_tender_button_create').click(this.proxy('action_def'));
       }
    },

    //--------------------------------------------------------------------------
    // Define Handler for new Custom Button
    // code ===> https://www.odoo.com/fr_FR/forum/aide-1/add-button-on-top-of-tree-view-32006
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
                    model: 'mcm_openedx.course_stat',
                    method: 'recherche',
                    args: ["", model_name, active_id],
                }).then(function (result) {
                    self.do_action(result);
                });
   },
});
});