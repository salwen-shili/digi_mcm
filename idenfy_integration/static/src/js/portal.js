odoo.define("idenfy_integration.portal", function (require) {
  "use strict";

  var publicWidget = require("web.public.widget");

  window.addEventListener("message", receiveMessage, false);
  function receiveMessage(event) {
    var website = $("#website").val;
    var url;
    if (website == "1") {
      url = "/charger_mes_documents";
    } else url = "/charger_mes_documents";
    console.log("start");
    console.log(event);
    console.log(this);
    var button = $("#submit_documents_next_button");
    var buttons = $("#document_next");
    console.log(button);
    console.log(buttons);
    console.log(event.data.status);
    if (event.data.status == "approved") {
      button.removeAttr("disabled");
    }
    if (event.data.status == "failed") {
      setTimeout(() => {
        window.location.href = "#popup1";
        window.setInterval(function () {
          var remainingTime = $("#spnSeconds").html();
          remainingTime = parseInt(remainingTime);
          if (remainingTime == 0) {
            location.href = url;
          } else {
            $("#spnSeconds").html(remainingTime - 1);
          }
        }, 1000);
      }, 2000);
    }
  }
});
