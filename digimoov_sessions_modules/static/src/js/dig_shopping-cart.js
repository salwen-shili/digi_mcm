document.addEventListener('DOMContentLoaded', function () {
  onchangeTextButton1();
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
  //end

  document
    .getElementById('cpf_video')
    .setAttribute('src', 'https://www.youtube.com/embed/PN7gVHdT7x4');
});

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
const sendData = (condition) => {
  sendHttpRequest('POST', '/shop/payment/update_condition', {
    params: {
      condition: condition,
    },
  })
    .then((responseData) => {})
    .catch((err) => {});
};

const addUserPlateform = () => {
  document.getElementById(
    'popupcontent'
  ).innerHTML = `<div style="text-align: -webkit-center;"><div class="spinner"></div></div>`;
  sendHttpRequest('POST', '/shop/adduser_plateform', {}).then((res) => {
    console.log(res.result.ajout);
    console.log(res.result.url);
    if (res.result.url.includes('https://')) {
      document.getElementById('popupcontent').innerHTML = `
                            <p style="margin-top: 12px;    text-align: center;">                              
                                 ${res.result.ajout}
                                 <br/>
                                  
                                </p>
                          
                        
                         <div style="text-align:center">
                            <a href="${res.result.url}"> <button type="button" class="btn btn-secondary action-button shake" style="padding: 6px 34px;"> Continuer </button></a>
                        </div>
                   
       
         `;
    } else {
      document.getElementById('popupcontent').innerHTML = `
                            <p style="margin-top: 12px;    text-align: center;">                              
                                 ${res.result.ajout}     
                                </p>
                          
                        
                         <div style="text-align:center">
                            <a href="#"> <button type="button" class="btn btn-secondary action-button" onclick="closepopup()" > Fermer </button></a>
                        </div>
                   
       
         `;
    }
  });

  //                        <div style="text-align:center">
  //                           <a href="${res.result.url}"> <button type="button" class="btn btn-secondary action-button" onclick="()=>window.location.href=${res.result.url} > Continuer </button></a>
  //                       </div>

  //        `;
  //     } else {
  //       document.getElementById('popupcontent').innerHTML = `
  //                           <p style="margin-top: 12px;    text-align: center;">
  //                                ${res.result.ajout}
  //                               </p>

  //                        <div style="text-align:center">
  //                           <a href="#"> <button type="button" class="btn btn-secondary action-button" onclick="closepopup()" > Fermer </button></a>
  //                       </div>

  //        `;
  //     }
  //   })

  //   .catch((err) => {
  //     console.log('error addUser', err);
  //   });
};
const cpfAccepted = () => {
  sendHttpRequest('POST', '/shop/cpf_accepted', {})
    .then((res) => {
      console.log('cpf_accepted', res.result.state);
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
      document.getElementById('centre_examen').value === 'all'
    ) {
      document
        .getElementById('pm_shop_checkout')
        .setAttribute('disabled', 'true');
      document.getElementById('pm_shop_checkout').classList.add('disabled');
      document
        .getElementById('pm_shop_checkout2')
        .setAttribute('disabled', 'true');
      document.getElementById('pm_shop_checkout2').classList.add('disabled');
    } else if (
      document.getElementById('options-date').value !== 'all' &&
      document.getElementById('centre_examen').value !== 'all'
    ) {
      document.getElementById('pm_shop_checkout').removeAttribute('disabled');
      document.getElementById('pm_shop_checkout').classList.remove('disabled');
      document.getElementById('pm_shop_checkout2').removeAttribute('disabled');
      document.getElementById('pm_shop_checkout2').classList.remove('disabled');
      document.getElementById('error_choix_date').style.display = 'none';
    }
  } else {
    document
      .getElementById('pm_shop_checkout')
      .setAttribute('disabled', 'true');
    document.getElementById('pm_shop_checkout').classList.add('disabled');
    document
      .getElementById('pm_shop_checkout2')
      .setAttribute('disabled', 'true');
    document.getElementById('pm_shop_checkout2').classList.add('disabled');
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

function msTracking(event, event_category, event_label, event_value) {
  (function (w, d, t, r, u) {
    var f, n, i;
    (w[u] = w[u] || []),
      (f = function () {
        var o = {
          ti: '134610618',
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

    if (optionsDate == 'all' || optionsDate == '') {
      return (document.getElementById('error_choix_date_popup').style.display =
        'inline-block');
    } else {
      document.getElementById('error_choix_date_popup').style.display = 'none';
    }
  }
  //here we are sure that user has selected the date
  //if condition de vente (checkbox_conditions) is checked - passer ou paiment ou mobiliser mon cpf
  var conditionCheckbox = document.getElementById('checkbox_conditions');
  var error = document.getElementById('error_conditions');
  if (conditionCheckbox.checked == true) {
    error.style.display = 'none';
    condition = true;
  } else {
    error.style.display = 'inline-block';
    condition = false;
  }
  if (condition == false) {
    return;
  }
  //redirection stripe
  stripe_pm = document.getElementById('stripe_pm');
  // console.log(stripe_pm, 'stripe_pm');
  if (stripe_pm) {
    if (stripe_pm.checked == true) {
      window.location.href = '/shop/checkout?express=1';
      return;
    }
  }
  // var state = 'accepted';
  var state = document.getElementById('state').value;
  console.log('***************state', state);

  if (cpf_pm) {
    // console.log(cpf_pm, 'cpf_pm');
    if (cpf_pm.checked == true) {
      if (cpf_pm.value == 'Formation pro') {
        switch (true) {
          case state.includes('https://www.moncompteformation.gouv.fr/'):
            msTracking(
              'clic sur mobiliser mon cpf pro status validé',
              'CPF',
              'Inscription CPF pro',
              '680'
            );
            window.location.href = state;
            break;
          case state == 'accepted':
            cpfAccepted();

            // document.getElementById('popupcontent').innerHTML = 'finished...';
            break;

          default:
            window.location.href = 'https://bit.ly/3nMlm2A';
            msTracking(
              'clic sur mobiliser mon cpf pro',
              'CPF',
              'Inscription CPF pro',
              '680'
            );
            break;
        }
      }
      if (cpf_pm.value == 'Formation premium') {
        switch (state) {
          case state.includes('https://www.moncompteformation.gouv.fr/'):
            msTracking(
              'clic sur mobiliser mon cpf premuim status validé',
              'CPF',
              'Inscription CPF premuim',
              '680'
            );
            break;
          case state == 'accepted':
            document.getElementById('popupcontent').innerHTML = 'wait...';
            cpfAccepted();

            document.getElementById('popupcontent').innerHTML = 'finished...';
            break;

          default:
            window.location.href = 'https://bit.ly/38IxvSa';
            msTracking(
              'clic sur mobiliser mon cpf premium',
              'CPF',
              'Inscription CPF Premium',
              '680'
            );
            break;
        }
      }
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
                            height: 40px;
                            width: 185px;
                            font-size: 15px;
                            background-color: #152856;
                            border: 1px solid hsl(240, 44%, 28%);
                            color: #ffffff;
                            font-weight: 600;
                            border-radius: 5px;
                            box-shadow: 0 2px 4px 0 rgba(87, 71, 81, 0.2);
                            cursor: pointer;
                            transition: all 2s ease-out;
                            transition: all 0.2s ease-out;
                            }
                            .action-button:hover,
                            .action-button:focus {
                            background-color: #ffffff;
                            border: 1px solid hsl(240, 44%, 28%);
                            color: #000000;
                            transition: all 0.2s ease-out;
                            }

                        </style>
                        

                        <div style="text-align:center">
                            <button type="button" class="btn btn-secondary action-button shake" id="continueBtn" onclick="verify_payment_method()">Continuer</button>
                        </div>`;
}
