document.addEventListener("DOMContentLoaded", function () {
  var formation = document.getElementById("cpf_pm").value;

  // var cpfTaxi =
  //   "https://www.moncompteformation.gouv.fr/espace-prive/html/#/formation/recherche/81121988000085_taxielearning/81121988000085_TAXI_ELEARNING";
  // var cpfVmdtr =
  //   "https://www.moncompteformation.gouv.fr/espace-prive/html/#/formation/recherche/81121988000085_VMDTR_Elearning/81121988000085_VMDTR_E-learning";
  // var cpfVtc =
  //   "https://www.moncompteformation.gouv.fr/espace-prive/html/#/formation/recherche/81121988000085_VTC_E-LEARNING/81121988000085_VTC_E-LEARNING";
  if (formation === "Formation à distance VTC") {
    var urlVtc = "https://www.youtube.com/embed/19BiYQVwZFs";
    document.getElementById("cpf_video").setAttribute("src", urlVtc);
  } else {
    document
      .getElementById("cpf_video")
      .setAttribute("src", "https://www.youtube.com/embed/vLIr9mckz8M");
  }
  //xmlhttprequest

  const sendHttpRequest = (method, url, data) => {
    const promise = new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open(method, url);

      xhr.responseType = "json";

      if (data) {
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
      }

      xhr.onload = () => {
        if (xhr.status >= 400) {
          reject(xhr.response);
        } else {
          resolve(xhr.response);
        }
      };

      xhr.onerror = () => {
        reject("Something went wrong!");
      };

      xhr.send(JSON.stringify(data));
    });
    return promise;
  };
  const sendData = (condition) => {
    sendHttpRequest("POST", "/shop/payment/update_condition", {
      params: {
        condition: condition,
      },
    })
      .then((responseData) => {})
      .catch((err) => {});
  };
  // fin xmlhttprequest

  onchangeTextButton1();

  //event listener on change sale conditions input
  // send post request to update sale conditions for the client on server
  // disable button if the checkboxcondition is false

  document
    .getElementById("checkbox_conditions")
    .addEventListener("change", function () {
      var condition = document.getElementById("checkbox_conditions").checked;
      var error = document.getElementById("error_conditions");
      var continueBtn = document.getElementById("continueBtn");
      if (condition) {
        continueBtn.removeAttribute("disabled");
        continueBtn.classList.remove("disabled");
        error.style.display = "none";

        sendData(condition);
      } else {
        continueBtn.setAttribute("disabled", "disabled");
        continueBtn.classList.add("disabled");
        error.style.display = "inline-block";
        sendData(condition);
      }
    });
  if (document.getElementById("promo_button")) {
    document.getElementById("promo_button").style.display = "inline";
  }
});

function onChangeCheckButton() {
  if (document.getElementById("options-date")) {
    if (
      document.getElementById("options-date").value === "all" ||
      document.getElementById("region_examen").value === "all"
    ) {
      document
        .getElementById("pm_shop_checkout")
        .setAttribute("disabled", "true");
      document.getElementById("pm_shop_checkout").classList.add("disabled");
    } else if (
      document.getElementById("options-date").value !== "all" &&
      document.getElementById("region_examen").value !== "all"
    ) {
      document.getElementById("pm_shop_checkout").removeAttribute("disabled");
      document.getElementById("pm_shop_checkout").classList.remove("disabled");
      document.getElementById("error_choix_date").style.display = "none";
    }
  } else {
    document
      .getElementById("pm_shop_checkout")
      .setAttribute("disabled", "true");
    document.getElementById("pm_shop_checkout").classList.add("disabled");
  }
}

function msTracking(event, event_category, event_label, event_value) {
  (function (w, d, t, r, u) {
    var f, n, i;
    (w[u] = w[u] || []),
      (f = function () {
        var o = {
          ti: "134601341",
        };
        (o.q = w[u]), (w[u] = new UET(o)), w[u].push("pageLoad");
      }),
      (n = d.createElement(t)),
      (n.src = r),
      (n.async = 1),
      (n.onload = n.onreadystatechange =
        function () {
          var s = this.readyState;
          (s && s !== "loaded" && s !== "complete") ||
            (f(), (n.onload = n.onreadystatechange = null));
        }),
      (i = d.getElementsByTagName(t)[0]),
      i.parentNode.insertBefore(n, i);
  })(window, document, "script", "//bat.bing.com/bat.js", "uetq");
  window.uetq = window.uetq || [];
  window.uetq.push("event", event, {
    event_category: event_category,
    event_label: event_label,
    event_value: event_value,
  });
}

function verify_payment_method() {
  //user can navigate #popup1 to the url directly so we need to secure
  //that he can't pass if he didn't choose a date
  if (!document.getElementById("options-date")) {
    return (document.getElementById("error_choix_date_popup").style.display =
      "inline-block");
  } else {
    var optionsDate = document.getElementById("options-date").value;
    console.log("verify", optionsDate);

    if (optionsDate == "all" || optionsDate == "") {
      return (document.getElementById("error_choix_date_popup").style.display =
        "inline-block");
    } else {
      document.getElementById("error_choix_date_popup").style.display = "none";
    }
  }
  //here we are sure that user has selected the date
  //if condition de vente (checkbox_conditions) is checked - passer ou paiment ou mobiliser mon cpf

  var conditionCheckbox = document.getElementById("checkbox_conditions");
  var error = document.getElementById("error_conditions");
  if (conditionCheckbox.checked == true) {
    error.style.display = "none";
    condition = true;
  } else {
    error.style.display = "inline-block";

    condition = false;
  }

  if (condition == false) {
    return;
  }

  stripe_pm = document.getElementById("stripe_pm");

  if (stripe_pm) {
    if (stripe_pm.checked == true) {
      window.location.href = "/shop/checkout?express=1";
    }
  }
  pole_emploi_pm = document.getElementById("pole_emploi_pm");
  if (pole_emploi_pm) {
    if (pole_emploi_pm.checked == true) {
      window.location.href = "/new/ticket/pole_emploi";
    }
  }
  cpf_pm = document.getElementById("cpf_pm");

  if (cpf_pm) {
    if (cpf_pm.checked == true) {
      if (cpf_pm.value == "Formation à distance TAXI") {
        window.location.href = "https://bit.ly/3DOiZG6";
        msTracking(
          "clic sur mobiliser mon cpf taxi",
          "CPF",
          "Inscription CPF TAXI",
          "680"
        );
        return;
      }
      if (cpf_pm.value == "Formation à distance VMDTR") {
        window.location.href = "https://bit.ly/3tbAxXw";
        msTracking(
          "clic sur mobiliser mon cpf vmdtr",
          "CPF",
          "Inscription CPF VMDTR",
          "849"
        );
        return;
      }
      if (cpf_pm.value == "Formation à distance VTC") {
        window.location.href = "https://bit.ly/3mZoImh";
        msTracking(
          "clic sur mobiliser mon cpf vtc",
          "CPF",
          "Inscription CPF VTC",
          "590"
        );
        return;
      }
    }
  }
}

//show popup if date is selected
function showPopup() {
  if (!document.getElementById("options-date")) {
    document.getElementById("error_no_date").style.display = "inline-block";
    return;
  }
  document.getElementById("error_no_date").style.display = "none";
  var optionsDate = document.getElementById("options-date").value;
  var cpfChecked = false;
  if (document.getElementById("cpf_pm")) {
    cpfChecked = document.getElementById("cpf_pm").checked;
  }
  var continueBtn = document.getElementById("continueBtn");
  var textbtn;
  cpfChecked
    ? (textbtn = "Mobiliser mon CPF")
    : (textbtn = "Passer au paiement");

  if (optionsDate != "all" && optionsDate != "") {
    document.getElementById("error_choix_date_popup").style.display = "none";
    continueBtn.innerText = textbtn;
    window.location.href = "#popup1";
  } else {
    document.getElementById("error_choix_date").style.display = "inline-block";
  }
}

//
function verify_checked() {
  var x = document.getElementById("checkbox_instalment");
  if (x) {
    if (document.getElementById("checkbox_instalment").checked == true) {
      document.getElementById("order_amount_to_pay").style.visibility =
        "visible";
      document.getElementById("order_instalment_number").style.visibility =
        "visible";
    } else {
      document.getElementById("order_amount_to_pay").style.visibility =
        "hidden";
      document.getElementById("order_instalment_number").style.visibility =
        "hidden";
    }
  }
}

//change button to mobiliser mon cpf or passer au paiment if cpf is checked or not
// according to that we show or hide cpf details and video

function onchangeTextButton() {
  if (document.getElementById("pm_shop_checkout2")) {
    document.getElementById("pm_shop_checkout2").innerText =
      "Mobiliser mon CPF";
  }
  if (document.getElementById("pm_shop_checkout")) {
    document.getElementById("pm_shop_checkout").innerText = "Mobiliser mon CPF";

    if (document.getElementById("promo_code")) {
      document.getElementById("promo_code").style.display = "none";
    }
    if (document.getElementById("promo_button")) {
      document.getElementById("promo_button").style.display = "none";
    }
    if (document.getElementById("promo_input")) {
      document.getElementById("promo_input").style.display = "none";
    }
    if (document.getElementById("order_instalment")) {
      document.getElementById("order_instalment").style.display = "none";
      document.getElementById("order_instalment_checkbox").style.display =
        "none";
      document.getElementById("order_instalment_number").style.display = "none";
      document.getElementById("order_instalment_number_order").style.display =
        "none";
      document.getElementById("order_amount_to_pay").style.display = "none";
      document.getElementById("order_amount_to_pay_amount").style.display =
        "none";
    }
  }
}
function onchangeTextButton1() {
  if (document.getElementById("pm_shop_checkout")) {
    document.getElementById("pm_shop_checkout").innerText =
      "Passer au paiement";
  }
  if (document.getElementById("pm_shop_checkout2")) {
    document.getElementById("pm_shop_checkout2").innerText =
      "Passer au paiement";
  }
  if (document.getElementById("cpf-details")) {
    document.getElementById("cpf-details").classList.add("hide");
    if (document.getElementById("arrow-down")) {
      document.getElementById("arrow-down").classList.add("hide");
    }
  }

  if (document.getElementById("pm_shop_checkout")) {
    if (document.getElementById("promo_code")) {
      document.getElementById("promo_code").style.display = "inline";
    } else {
      document.getElementById("promo_input").style.display = "inline";
      document.getElementById("promo_button").style.display = "inline";
    }

    if (document.getElementById("order_instalment")) {
      document.getElementById("order_instalment").style.display = "block";
      document.getElementById("order_instalment_checkbox").style.display =
        "table-cell";
    }
    instalment = document.getElementById("checkbox_instalment");
    if (instalment) {
      if (instalment.checked == true) {
        document.getElementById("order_instalment_number").style.display =
          "block";
        document.getElementById("order_instalment_number_order").style.display =
          "table-cell";
        document.getElementById("order_amount_to_pay").style.display = "block";
        document.getElementById("order_amount_to_pay_amount").style.display =
          "table-cell";
      }
    }
  }
}
