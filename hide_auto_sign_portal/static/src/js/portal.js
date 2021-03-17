odoo.define('hide_auto_sign_portal.portal', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.SignTemplate = publicWidget.Widget.extend({
     selector: '.o_portal_sidebar',
     events: {
        'click a[id="accept_and_sign"]': 'hide_auto_sign',
        'mouseover a[id="accept_and_sign"]': 'hide_auto_sign',
        'click a[id="footer_accept_and_sign"]': 'hide_auto_sign',
        'mouseover a[id="footer_accept_and_sign"]': 'hide_auto_sign',
    },
    start: function() {
         var self = this;
         this.$('a.o_web_sign_auto_button').css('display','none');
         this.$('a.o_web_sign_load_button').css('display','none');
         this.$('a.o_web_sign_draw_button').html('Dessiner votre signature');
    },
    hide_auto_sign: function (ev) {
         var self = this;
         this.$('a.o_web_sign_auto_button').css('display','none');
         this.$('a.o_web_sign_load_button').css('display','none');
         this.$('a.o_web_sign_draw_button').html('Dessiner votre signature');
    },
    });
});