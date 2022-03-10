odoo.define('idenfy_integration.portal', function (require) {
  ('use strict');

  var publicWidget = require('web.public.widget');

  window.addEventListener('message', receiveMessage, false);
  function receiveMessage(event) {
    var button = $('#submit_documents_next_button');
    var button = $('#submit_documents_next_button');

    //console.log('start');
    //console.log(event);
    //console.log(this);
    var button = $('#submit_documents_next_button');
    var buttons = $('#document_next');
    //console.log(button);
    //console.log(buttons);
    //console.log(event.data.status);
    if (event.data.status == 'approved') {
      button.removeAttr('disabled');
    }
    if (event.data.status == 'failed') {
      if (window.location.pathname == '/charger_mes_documents') {
        //console.log(
        //   'localstorage',
        //   localStorage.getItem('failed_status_counter')
        // );
        var popup = $('#idenfy_popup');
        var statusCounter = localStorage.getItem('failed_status_counter');
        //second try redirect to manual upload
        if (parseInt(statusCounter) == 1) {
          localStorage.setItem('failed_status_counter', 0);
          //console.log($('#notifMessage'));
          //console.log('idenfy message');
          $('#notifMessage').text(
            "L'identification automatique et la vérification de l'authenticité vos documents n'a pas pu se faire. Vous serez redirigé pour charger vos documents manuellement"
          );
          popup.addClass('popup_show');
          var counter = setInterval(function () {
            var remainingTime = $('#popup_counter').html();
            remainingTime = parseInt(remainingTime);
            if (remainingTime == 0) {
              window.location.href = '/charger_mes_documents_manual';
              clearInterval(counter);
            } else {
              $('#popup_counter').html(remainingTime - 1);
            }
          }, 1000);
        }
        //first try
        else {
          localStorage.setItem('failed_status_counter', 1);
          //refraichir la page
          //console.log('idenfy message');
          $('#notifMessage').text(
            `L'identification automatique et la vérification de l'authenticité vos documents n'a pas pu se faire. Vous allez réessayer dans quelques instant`
          );
          popup.addClass('popup_show');
          var counter = setInterval(function () {
            var remainingTime = $('#popup_counter').html();
            remainingTime = parseInt(remainingTime);
            if (remainingTime == 0) {
              window.location.reload();
              clearInterval(counter);
            } else {
              $('#popup_counter').html(remainingTime - 1);
            }
          }, 1000);
        }
      }
    }
  }
});
