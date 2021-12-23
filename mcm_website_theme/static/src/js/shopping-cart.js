document.addEventListener('DOMContentLoaded', function () {
  var formation = document.getElementById('cpf_pm').value;
  if (formation === 'Formation à distance VTC') {
    var urlVtc = 'https://www.youtube.com/embed/19BiYQVwZFs';
    document.getElementById('cpf_video').setAttribute('src', urlVtc);
  } else {
    document
      .getElementById('cpf_video')
      .setAttribute('src', 'https://www.youtube.com/embed/vLIr9mckz8M');
  }

  onchangeTextButton1();

  //event listener on change sale conditions input
  // send post request to update sale conditions for the client on server
  // disable button if the checkboxcondition is false

  document
    .getElementById('checkbox_conditions')
    .addEventListener('change', function () {
      var condition = document.getElementById('checkbox_conditions').checked;
      var error = document.getElementById('error_conditions');
      var continueBtn = document.getElementById('continueBtn');
      if (condition) {
        continueBtn.removeAttribute('disabled');
        continueBtn.classList.remove('disabled');
        error.style.display = 'none';

        sendData(condition);
      } else {
        continueBtn.setAttribute('disabled', 'disabled');
        continueBtn.classList.add('disabled');
        error.style.display = 'inline-block';
        sendData(condition);
      }
    });
  if (document.getElementById('promo_button')) {
    document.getElementById('promo_button').style.display = 'inline';
  }
});

//animation
const sendData = (condition) => {
  sendHttpRequest('POST', '/shop/payment/update_condition', {
    params: {
      condition: condition,
    },
  })
    .then((responseData) => {})
    .catch((err) => {});
};
var colors = ['#000000', '#fdd105', '#959595', '#d5a376', '#ff1e00'];
function frame() {
  confetti({
    particleCount: 2,
    angle: 60,
    spread: 55,
    origin: { x: 0 },
    colors: colors,
  });
  confetti({
    particleCount: 2,
    angle: 120,
    spread: 55,
    origin: { x: 1 },
    colors: colors,
  });
}
//xmlhttprequest
const sendHttpRequest = (method, url, data) => {
  const promise = new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url);

    xhr.responseType = 'json';

    if (data) {
      xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    }

    xhr.onload = () => {
      if (xhr.status >= 400) {
        reject(xhr.response);
      } else {
        resolve(xhr.response);
      }
    };

    xhr.onerror = () => {
      reject('Something went wrong!');
    };

    xhr.send(JSON.stringify(data));
  });
  return promise;
};
const addUserPlateform = () => {
  document.getElementById(
    'popupcontent'
  ).innerHTML = `<div style="text-align: -webkit-center;"><div class="spinner"></div></div>`;
  sendHttpRequest('POST', '/shop/adduser_plateform', {}).then((res) => {
    console.log('res.result.url');

    if (res.result.url) {
      if (res.result.url.includes('https://')) {
        for (let index = 0; index < 200; index++) {
          frame();
        }
        document.getElementById('popupcontent').innerHTML = `
                            <p style="margin-top: 12px; text-align: center;">                              
                                 ${res.result.ajout}
                                 <br/>
                                </p>
                         <div style="text-align:center">
                            <a href="${res.result.url}"> <button type="button" class="btn btn-secondary action-button shake" style="padding: 6px 34px;"> Continuer </button></a>
                        </div>     
         `;
      }
    } else {
      if (res.result.ajout) {
        //js-container-animation to animate
        if (res.result.url) {
          document.getElementById('popupcontent').innerHTML = `
                            <p  style="margin-top: 12px;text-align: justify;">                              
                                 ${res.result.ajout}     
                            </p>
                            <div style="text-align:center">
                                <a href="#"> <button type="button" class="btn btn-secondary action-button" onclick="closepopup()"  style="padding: 8px 29px;" > Fermer </button></a>

                            </div>
         `;
        }
        document.getElementById('popupcontent').innerHTML = `
                            <p style="margin-top: 12px;text-align: justify;">                              
                                 ${res.result.ajout}     
                            </p>
                            <div style="text-align:center">
                                <a href="#"> <button type="button" class="btn btn-secondary action-button"  onclick="closepopup()" style="padding: 8px 29px;" > Fermer </button></a>
                            </div>
         `;
      }
      if (
        res.result.ajout &&
        res.result.ajout ==
          'Vous avez choisi de préserver votre droit de rétractation sous un délai de 14 jours. Si vous souhaitez renoncer à ce droit et commencer votre formation dés maintenant, veuillez cliquer sur continuer.'
      ) {
        document.getElementById('popupcontent').innerHTML = `
                            <p style="margin-top: 12px;text-align: justify;">                              
                                 ${res.result.ajout}     
                            </p>
                            <div style="text-align:center">
                                <button type="button" class="btn btn-secondary action-button" id="Précédent" onclick="closepopup()" style="padding: 8px 29px;">Précédent</button>
                                <button type="button" class="btn btn-secondary action-button shake" style="padding: 8px 29px;     margin-left: 11px;" onclick="renonce()" > Continuer </button>
                            </div>

         `;
      }
    }
  });
};
const cpfAccepted = () => {
  sendHttpRequest('POST', '/shop/cpf_accepted', {})
    .then((res) => {
      if (res.result.state) {
        addUserPlateform();
      }
    })
    .catch((err) => {
      console.log(err);
    });
};

function onChangeCheckButton() {
  if (document.getElementById('options-date')) {
    if (
      document.getElementById('options-date').value === 'all' ||
      document.getElementById('region_examen').value === 'all'
    ) {
      document
        .getElementById('pm_shop_checkout')
        .setAttribute('disabled', 'true');
      document.getElementById('pm_shop_checkout').classList.add('disabled');
    } else if (
      document.getElementById('options-date').value !== 'all' &&
      document.getElementById('region_examen').value !== 'all'
    ) {
      document.getElementById('pm_shop_checkout').removeAttribute('disabled');
      document.getElementById('pm_shop_checkout').classList.remove('disabled');
      document.getElementById('error_choix_date').style.display = 'none';
    }
  } else {
    document
      .getElementById('pm_shop_checkout')
      .setAttribute('disabled', 'true');
    document.getElementById('pm_shop_checkout').classList.add('disabled');
  }
}

function msTracking(event, event_category, event_label, event_value) {
  (function (w, d, t, r, u) {
    var f, n, i;
    (w[u] = w[u] || []),
      (f = function () {
        var o = {
          ti: '134601341',
        };
        (o.q = w[u]), (w[u] = new UET(o)), w[u].push('pageLoad');
      }),
      (n = d.createElement(t)),
      (n.src = r),
      (n.async = 1),
      (n.onload = n.onreadystatechange =
        function () {
          var s = this.readyState;
          (s && s !== 'loaded' && s !== 'complete') ||
            (f(), (n.onload = n.onreadystatechange = null));
        }),
      (i = d.getElementsByTagName(t)[0]),
      i.parentNode.insertBefore(n, i);
  })(window, document, 'script', '//bat.bing.com/bat.js', 'uetq');
  window.uetq = window.uetq || [];
  window.uetq.push('event', event, {
    event_category: event_category,
    event_label: event_label,
    event_value: event_value,
  });
}

function verify_payment_method() {
  //user can navigate #popup1 to the url directly so we need to secure
  //that he can't pass if he didn't choose a date
  if (!document.getElementById('options-date')) {
    return (document.getElementById('error_choix_date_popup').style.display =
      'inline-block');
  } else {
    var optionsDate = document.getElementById('options-date').value;
    console.log('verify', optionsDate);

    if (optionsDate == 'all' || optionsDate == '') {
      return (document.getElementById('error_choix_date_popup').style.display =
        'inline-block');
    } else {
      document.getElementById('error_choix_date_popup').style.display = 'none';
    }
  }
  //here we are sure that user has selected the date
  //if condition de vente (checkbox_conditions) is checked - passer ou paiment ou mobiliser mon cpf

  var conditionCheckbox;
  if (document.getElementById('checkbox_conditions')) {
    conditionCheckbox = document.getElementById('checkbox_conditions');
    var error = document.getElementById('error_conditions');
    if (conditionCheckbox && conditionCheckbox.checked == true) {
      error.style.display = 'none';
      condition = true;
    } else {
      error.style.display = 'inline-block';

      condition = false;
    }

    if (condition == false) {
      return;
    }
  }

  stripe_pm = document.getElementById('stripe_pm');

  if (stripe_pm) {
    if (stripe_pm.checked == true) {
      window.location.href = '/shop/checkout?express=1';
    }
  }
  pole_emploi_pm = document.getElementById('pole_emploi_pm');
  if (pole_emploi_pm) {
    if (pole_emploi_pm.checked == true) {
      window.location.href = '/new/ticket/pole_emploi';
    }
  }
  cpf_pm = document.getElementById('cpf_pm');
  // var state = 'accepted';
  var state = document.getElementById('state').value;
  console.log('***************state', state);
  if (cpf_pm) {
    if (cpf_pm.checked == true) {
      if (cpf_pm.value == 'Formation à distance TAXI') {
        switch (true) {
          case state.includes('https://www.moncompteformation.gouv.fr/'):
            msTracking(
              'clic sur mobiliser mon cpf Formation à distance TAXI status validé',
              'CPF',
              'Inscription CPF Formation à distance TAXI',
              '680'
            );
            window.location.href = state;
            break;
          case state == 'accepted':
            cpfAccepted();
            break;

          default:
            window.location.href = 'https://bit.ly/3DOiZG6';
            msTracking(
              'clic sur mobiliser mon cpf taxi',
              'CPF',
              'Inscription CPF TAXI',
              '680'
            );
            break;
        }

        return;
      }
      if (cpf_pm.value == 'Formation à distance VMDTR') {
        switch (true) {
          case state.includes('https://www.moncompteformation.gouv.fr/'):
            msTracking(
              'clic sur mobiliser mon cpf Formation à distance TAXI status validé',
              'CPF',
              'Inscription CPF Formation à distance TAXI',
              '680'
            );
            window.location.href = state;
            break;
          case state == 'accepted':
            cpfAccepted();
            break;

          default:
            window.location.href = 'https://bit.ly/3tbAxXw';
            msTracking(
              'clic sur mobiliser mon cpf vmdtr',
              'CPF',
              'Inscription CPF VMDTR',
              '849'
            );
            break;
        }

        return;
      }
      if (cpf_pm.value == '[vtc] Formation à distance VTC') {
        switch (true) {
          case state.includes('https://www.moncompteformation.gouv.fr/'):
            msTracking(
              'clic sur mobiliser mon cpf Formation à distance TAXI status validé',
              'CPF',
              'Inscription CPF Formation à distance TAXI',
              '680'
            );
            window.location.href = state;
            break;
          case state == 'accepted':
            cpfAccepted();
            console.log('cpf accepted');
            break;

          default:
            window.location.href = 'https://bit.ly/3mZoImh';
            msTracking(
              'clic sur mobiliser mon cpf vtc',
              'CPF',
              'Inscription CPF VTC',
              '590'
            );
            break;
        }

        return;
      }
    }
  }
}

//show popup if date is selected
function showPopup() {
  if (!document.getElementById('options-date')) {
    document.getElementById('error_no_date').style.display = 'inline-block';
    return;
  }
  document.getElementById('error_no_date').style.display = 'none';
  var optionsDate = document.getElementById('options-date').value;
  var cpfChecked = false;
  if (document.getElementById('cpf_pm')) {
    cpfChecked = document.getElementById('cpf_pm').checked;
  }
  var continueBtn = document.getElementById('continueBtn');
  var textbtn;
  cpfChecked
    ? (textbtn = 'Mobiliser mon CPF')
    : (textbtn = 'Passer au paiement');

  if (optionsDate != 'all' && optionsDate != '') {
    document.getElementById('error_choix_date_popup').style.display = 'none';
    continueBtn.innerText = textbtn;
    window.location.href = '#popup1';
  } else {
    document.getElementById('error_choix_date').style.display = 'inline-block';
  }
}

//
function verify_checked() {
  var x = document.getElementById('checkbox_instalment');
  if (x) {
    if (document.getElementById('checkbox_instalment').checked == true) {
      document.getElementById('order_amount_to_pay').style.visibility =
        'visible';
      document.getElementById('order_instalment_number').style.visibility =
        'visible';
    } else {
      document.getElementById('order_amount_to_pay').style.visibility =
        'hidden';
      document.getElementById('order_instalment_number').style.visibility =
        'hidden';
    }
  }
}

function closepopup() {
  console.log('closepopup');
  document.getElementById('popupcontent').innerHTML = `
  <p id="notifMessage">
                            <div class="input checkbox" style="width:90%">
                                <input type="checkbox" id="checkbox_failures" style="white-space: nowrap;" class="text-xl-left border-0" t-att-checked="website_sale_order.failures" t-att-value="website_sale_order.failures">
                                    <label for="failures" style="display:inline">
                                        Je souhaite accéder à la formation dès maintenant sans attendre 14 jours. Je reconnais que
                                        <span t-if="website_sale_order.company_id.id==2">DIGIMOOV</span>
                                        <span t-if="website_sale_order.company_id.id==1">MCM Academy</span>
                                        procédera à l'exécution immédiate de ma formation en ligne et à ce titre, je
                            renonce expressément à exercer mon droit de rétractation conformément aux dispositions de
                            l'article L.221-28 1° du code de la consommation.
                                    </label>
                                </input>
                            </div>
                            <div class="input checkbox" style="margin-top: 12px;">
                                <input type="checkbox" id="checkbox_conditions" style="white-space: nowrap;" class="text-xl-left border-0" t-att-checked="website_sale_order.conditions" t-att-value="website_sale_order.conditions">
                                    <label for="conditions" style="display:inline">
                                        J'ai lu et j'accepte les
                                        <a href="/conditions" target="blank" style="font-weight: 600; color: #000;">
                                            conditions générales de vente
                                        </a>
                                    </label>
                                </input>
                            </div>
                            <p id="error_conditions" class="alert alert-warning" style="margin-left:0%;display:none;">
                                Vous devez acceptez les conditions générales de ventes
                            </p>

                            <p id="error_choix_date_popup" class="alert alert-warning" style="margin-left:0%;display:none;">
                                Vous devez fermer cette fenêtre et selectionner votre date d'examen
                            </p>
                        </p>
                        <style>
                            .action-button {
                            width: 153px;
                            background: #262223;
                            font-weight: bold;
                            color: white;
                            border: 0 none;
                            border-radius: 0px;
                            padding: 10px 5px;
                            }

                            .action-button:hover,
                            .action-button:focus {
                            background: #e6e6e6;
                            font-weight: bold;
                            color: black;
                            cursor: pointer;       
                            }

                        </style>
                        

                        <div style="text-align:center">
                            <button type="button" class="btn btn-secondary action-button shake" id="continueBtn" onclick="verify_payment_method()">Continuer</button>
                        </div>`;
}

//change button to mobiliser mon cpf or passer au paiment if cpf is checked or not
// according to that we show or hide cpf details and video

function onchangeTextButton() {
  if (document.getElementById('pm_shop_checkout2')) {
    document.getElementById('pm_shop_checkout2').innerText =
      'Mobiliser mon CPF';
  }
  if (document.getElementById('pm_shop_checkout')) {
    document.getElementById('pm_shop_checkout').innerText = 'Mobiliser mon CPF';

    if (document.getElementById('promo_code')) {
      document.getElementById('promo_code').style.display = 'none';
    }
    if (document.getElementById('promo_button')) {
      document.getElementById('promo_button').style.display = 'none';
    }
    if (document.getElementById('promo_input')) {
      document.getElementById('promo_input').style.display = 'none';
    }
    if (document.getElementById('order_instalment')) {
      document.getElementById('order_instalment').style.display = 'none';
      document.getElementById('order_instalment_checkbox').style.display =
        'none';
      document.getElementById('order_instalment_number').style.display = 'none';
      document.getElementById('order_instalment_number_order').style.display =
        'none';
      document.getElementById('order_amount_to_pay').style.display = 'none';
      document.getElementById('order_amount_to_pay_amount').style.display =
        'none';
    }
  }
}
function onchangeTextButton1() {
  if (document.getElementById('pm_shop_checkout')) {
    document.getElementById('pm_shop_checkout').innerText =
      'Passer au paiement';
  }
  if (document.getElementById('pm_shop_checkout2')) {
    document.getElementById('pm_shop_checkout2').innerText =
      'Passer au paiement';
  }
  if (document.getElementById('cpf-details')) {
    document.getElementById('cpf-details').classList.add('hide');
    if (document.getElementById('arrow-down')) {
      document.getElementById('arrow-down').classList.add('hide');
    }
  }

  if (document.getElementById('pm_shop_checkout')) {
    if (document.getElementById('promo_code')) {
      document.getElementById('promo_code').style.display = 'inline';
    } else {
      document.getElementById('promo_input').style.display = 'inline';
      document.getElementById('promo_button').style.display = 'inline';
    }

    if (document.getElementById('order_instalment')) {
      document.getElementById('order_instalment').style.display = 'block';
      document.getElementById('order_instalment_checkbox').style.display =
        'table-cell';
    }
    instalment = document.getElementById('checkbox_instalment');
    if (instalment) {
      if (instalment.checked == true) {
        document.getElementById('order_instalment_number').style.display =
          'block';
        document.getElementById('order_instalment_number_order').style.display =
          'table-cell';
        document.getElementById('order_amount_to_pay').style.display = 'block';
        document.getElementById('order_amount_to_pay_amount').style.display =
          'table-cell';
      }
    }
  }
}

function renonce() {
  document.getElementById('popupcontent').innerHTML = `
                                                     
                                 <p id="notifMessage">

                            <div class="input checkbox" style="width:90%">
                                <input type="checkbox" id="checkbox_failures" style="white-space: nowrap;" class="text-xl-left border-0" t-att-checked="website_sale_order.failures" t-att-value="website_sale_order.failures">
                                    <label for="failures" style="display:inline">
                                        Je souhaite accéder à la formation dès maintenant sans attendre 14 jours. Je reconnais que
                                        <span t-if="website_sale_order.company_id.id==2">DIGIMOOV</span>
                                        <span t-if="website_sale_order.company_id.id==1">MCM Academy</span>
                                        procédera à l'exécution immédiate de ma formation en ligne et à ce titre, je
                            renonce expressément à exercer mon droit de rétractation conformément aux dispositions de
                            l'article L.221-28 1° du code de la consommation.
                                    </label>
                                </input>
                            </div>
                            
                            <p id="error_conditions" class="alert alert-warning" style="margin-left:0%;display:none;">
                                Vous devez acceptez les conditions générales de ventes
                            </p>

                            <p id="error_choix_date_popup" class="alert alert-warning" style="margin-left:0%;display:none;">
                                Vous devez fermer cette fenêtre et selectionner votre date d'examen
                            </p>
                        </p> 
                       
                          
                            <div style="text-align:center">
                             <button type="button" class="btn btn-secondary action-button" id="Précédent"  style="padding: 8px 29px;" onclick="cpfAccepted()">Précédent</button>
                             <button type="button" class="btn btn-secondary action-button shake" id="continueBtn" onclick="verify_payment_method()"style="padding: 8px 29px  ;   margin-left: 11px;">Continuer</button>
                          </div>
         `;
}
