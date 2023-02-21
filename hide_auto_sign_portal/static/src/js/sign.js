odoo.define('hide_auto_sign_portal.Signature', function (require) {
'use strict';
var core = require('web.core');
var ajax = require('web.ajax');
var qweb = core.qweb;
// console.log('aaaaaaaaaaaaaaaaaaaaaaa');
ajax.loadXML('/hide_auto_sign_portal/static/src/xml/hide_auto_sign_portal.xml', qweb);
});