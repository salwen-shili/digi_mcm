odoo.define('idenfy_integration.portal', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

window.addEventListener("message", receiveMessage, false);
            function receiveMessage(event) {
            console.log('start');
            console.log(event);
            console.log(this);
            var button = $('#submit_documents_next_button');
            var buttons = $('#document_next');
            console.log(button);
            console.log(buttons);
            console.log(event.data.status);
            if (event.data.status == 'approved'){
                        button.removeAttr("disabled")
            }
    }
});