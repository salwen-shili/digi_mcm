document.addEventListener('DOMContentLoaded', function () {
  displayInstalmentPayment();
  onchangeTextButton1();
  document.getElementById('checkbox_conditions').addEventListener('change', function () {
    var condition = document.getElementById('checkbox_conditions').checked;
    var error = document.getElementById('error_conditions');
    var continueBtn = document.getElementById('continueBtn');
    if (condition) {
      continueBtn.removeAttribute('disabled');
      continueBtn.classList.remove('disabled');
      error.style.display = 'none';

      updateCondition(condition);
    } else {
      continueBtn.setAttribute('disabled', 'disabled');
      continueBtn.classList.add('disabled');
      error.style.display = 'inline-block';
      updateCondition(condition);
    }
  });
  //end

  document
    .getElementById('cpf_video')
    .setAttribute('src', 'https://www.youtube.com/embed/PN7gVHdT7x4');

  //event on click on checkbox paiement installment
  document.getElementById('checkbox_instalment').addEventListener('click', function () {
    displayInstalmentPayment();
  });
});

//animation
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

const updateCondition = (condition) => {
  sendHttpRequest('POST', '/shop/payment/update_condition', {
    params: {
      condition: condition,
    },
  })
    .then((responseData) => {})
    .catch((err) => {});
};

//adduserplateform
const addUserPlateform = () => {
  document.getElementById(
    'popupcontent'
  ).innerHTML = `<div style="text-align: -webkit-center;"><div class="spinner"></div></div>`;
  sendHttpRequest('POST', '/shop/adduser_plateform', {}).then((res) => {
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
                            <a onclick='window.open("${res.result.url}");return false;'> <button type="button" class="btn btn-secondary action-button shake" style="padding: 6px 34px;"> Continuer </button></a>
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
                                <button type="button" class="btn btn-secondary action-button" id="non_renonce" style="padding: 7.5px 38.5px;" onclick="closepopup('/my/home')">Attendre 14 jours</button>
                                <button type="button" class="btn btn-secondary action-button shake" style="padding: 7.5px 38.5px;" onclick="renonce()" > Continuer </button>
                            </div>
         `;
      }
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
//cpf accepted
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
  hideAlertDate();

  if (document.getElementById('options-date')) {
    //No session available
    if (
      document.getElementById('options-date').value === 'all' ||
      document.getElementById('centre_examen').value === 'all'
    ) {
      // console.log(document.getElementById('options-date'));
      document.getElementById('pm_shop_checkout').setAttribute('disabled', 'true');
      document.getElementById('pm_shop_checkout').classList.add('disabled');
      document.getElementById('pm_shop_checkout2').setAttribute('disabled', 'true');
      document.getElementById('pm_shop_checkout2').classList.add('disabled');
    }
    //we have available sessions
    else if (
      document.getElementById('options-date').value !== 'all' &&
      document.getElementById('centre_examen').value !== 'all'
    ) {
      document.getElementById('pm_shop_checkout').removeAttribute('disabled');
      document.getElementById('pm_shop_checkout').classList.remove('disabled');
      document.getElementById('pm_shop_checkout2').removeAttribute('disabled');
      document.getElementById('pm_shop_checkout2').classList.remove('disabled');
      document.getElementById('error_choix_date').style.display = 'none';
      //available session ===> check if we have surpassed 4 months
      // const sel = document.getElementById('options-date');
      // const isAccessible = sessionIsAccessible(sel.options[sel.selectedIndex].text);
      // if (isAccessible) {
      //   disablePaymentButton();
      // }

      // get selected option and show/hide alert for session >4 months
      const sel = document.getElementById('options-date');

      sessionIsAccessible(sel.options[sel.selectedIndex].getAttribute('data'));
    }
  } else {
    document.getElementById('pm_shop_checkout').setAttribute('disabled', 'true');
    document.getElementById('pm_shop_checkout').classList.add('disabled');
    document.getElementById('pm_shop_checkout2').setAttribute('disabled', 'true');
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

  var polechecked = false;
  if (document.getElementById('pole_emploi_checkbox')) {
    polechecked = pole_emploi_checkbox.checked;
  }
  cpfChecked || polechecked
    ? (textbtn = 'Mobiliser mon CPF')
    : (textbtn = 'Passer au paiement');

  if (optionsDate != 'all' && optionsDate != '') {
    if (document.getElementById('error_choix_date_popup')) {
      document.getElementById('error_choix_date_popup').style.display = 'none';
    }

    continueBtn.innerText = textbtn;
    window.location.href = '#popup1';
  } else {
    if (document.getElementById('error_choix_date')) {
      document.getElementById('error_choix_date').style.display = 'inline-block';
    }
  }
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
      if (document.getElementById('error_choix_date_popup')) {
        document.getElementById('error_choix_date_popup').style.display = 'none';
      }
    }
  }
  //here we are sure that user has selected the date
  //if condition de vente (checkbox_conditions) is checked - passer ou paiment ou mobiliser mon cpf
  var conditionCheckbox;
  var error;
  if (document.getElementById('checkbox_conditions')) {
    conditionCheckbox = document.getElementById('checkbox_conditions');
    error = document.getElementById('error_conditions');
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

  if (cpf_pm) {
    // console.log(cpf_pm, 'cpf_pm');
    if (cpf_pm.checked == true || pole_emploi_checkbox.checked == true) {
      if (cpf_pm.value == 'Formation pro') {
        switch (true) {
          case state.includes('https://www.moncompteformation.gouv.fr/'):
            window.open(state, '_blank');
            break;
          case state == 'accepted':
            cpfAccepted();

            // document.getElementById('popupcontent').innerHTML = 'finished...';
            break;

          default:
            window.open('https://bit.ly/3uLde9W', '_blank');

            break;
        }
        return;
      }
      if (cpf_pm.value == 'Formation premium') {
        switch (true) {
          case state.includes('https://www.moncompteformation.gouv.fr/'):
            window.open(state, '_blank');
            break;
          case state == 'accepted':
            cpfAccepted();
            break;

          default:
            window.open('https://bit.ly/3LJQLQP', '_blank');

            break;
        }
        return;
      }
    }
  }
}

function closepopup(msg) {
  if (msg) {
    window.location.href = msg;
    return;
  }
  document.getElementById('popupcontent').innerHTML = `
  <p id="notifMessage">
                            <div class="input checkbox" style="width:90%">
                                <input type="checkbox" id="checkbox_failures" style="white-space: nowrap;" class="text-xl-left border-0" t-att-checked="website_sale_order.failures" t-att-value="website_sale_order.failures">
                                    <label for="failures" style="display:inline">
                                        Je souhaite accéder à la formation dès maintenant sans attendre 14 jours. Je reconnais que DIGIMOOV procédera à l'exécution immédiate de ma formation en ligne et à ce titre, je
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
                        <a href="#">  
                        <button type="button" class="btn btn-secondary action-button" id="Précédent"  style="padding: 8px 29px;">Fermer</button>
                        </a>
                            <button type="button" class="btn btn-secondary action-button shake" id="continueBtn" onclick="verify_payment_method()">Continuer</button>
                        </div>`;
}

function renonce() {
  document.getElementById('popupcontent').innerHTML = `
                                                     
                                 <p id="notifMessage">

                            <div class="input checkbox" style="width:90%">
                                <input type="checkbox" id="checkbox_failures" style="white-space: nowrap;" class="text-xl-left border-0" t-att-checked="website_sale_order.failures" t-att-value="website_sale_order.failures">
                                    <label for="failures" style="display:inline">
                                        Je souhaite accéder à la formation dès maintenant sans attendre 14 jours. Je reconnais que DIGIMOOV
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
                             <button type="button" class="btn btn-secondary action-button shake" id="continueBtn" onclick="verify_payment_method()"style="padding: 8px 29px;">Continuer</button>
                          </div>
         `;
}

// Création d'une fonction showpoleemploidetails pour afficher les détails de pole emploi et hidepoleemploidetails pour masquer les détails pole emploi.
// Création d'une fonction sendpoleemploistate qui récupère l'état de radio button et envoyer cet état au backend avec un post request vers /shop/cart/update_pole_emploi  (checked : true ou false)
// Cette méthode est utilise à chaque clic d'un radio button
const sendPoleEmploiState = (pole_emploi_state) => {
  sendHttpRequest('POST', '/shop/cart/update_pole_emploi', {
    params: {
      pole_emploi_state: pole_emploi_state,
    },
  })
    .then((res) => {
      console.log(res);
    })
    .catch((err) => {
      console.log(err);
    });
};

//hide pole emploie details
function hidePoleEmploiDetails() {
  if (document.getElementById('pole-emploi-details')) {
    document.getElementById('pole-emploi-details').classList.add('hide');
    if (document.getElementById('arrow-down-pole-emploi')) {
      document.getElementById('arrow-down-pole-emploi').classList.add('hide');
    }
  }
}
//show pole emploie details
function showPoleEmploiDetails() {
  if (document.getElementById('pole-emploi-details')) {
    document.getElementById('pole-emploi-details').classList.remove('hide');
    if (document.getElementById('arrow-down-pole-emploi')) {
      document.getElementById('arrow-down-pole-emploi').classList.remove('hide');
    }
  }
}

//hide pole emploie details
function hideCpfDetails() {
  if (document.getElementById('cpf-details')) {
    document.getElementById('cpf-details').classList.add('hide');
    if (document.getElementById('arrow-down')) {
      document.getElementById('arrow-down').classList.add('hide');
    }
  }
}
//show pole emploie details
function showCpfDetails() {
  if (document.getElementById('cpf-details')) {
    document.getElementById('cpf-details').classList.remove('hide');
    if (document.getElementById('arrow-down')) {
      document.getElementById('arrow-down').classList.remove('hide');
    }
  }
}

//on click cpf / carte bleu
function onchangeTextButton() {
  //hide cpf details when pole_emploi is checked

  if (pole_emploi_checkbox) {
    if (pole_emploi_checkbox.checked) {
      //hide instalment

      //send pole emploi checked = true
      //hide cpf details
      hideCpfDetails();
      //show pole emploi details
      showPoleEmploiDetails();
      sendPoleEmploiState(pole_emploi_checkbox.checked);
      if (document.getElementById('cpf-details')) {
        document.getElementById('cpf-details').classList.add('hide');
        if (document.getElementById('arrow-down')) {
          document.getElementById('arrow-down').classList.add('hide');
        }
      }
    } else {
      //hide poleEmploi details
      hidePoleEmploiDetails();
      //send pole emploi checked
      sendPoleEmploiState(pole_emploi_checkbox.checked);
    }
  }
  var stripe_pm = document.getElementById('stripe_pm');
  if (stripe_pm) {
    if (stripe_pm.checked == true) {
      document.getElementById('pm_shop_check').href = '/shop/checkout?express=1';

      document.getElementById('pm_shop_checkout').href = '/shop/checkout?express=1';
    }
  }
  cpf_pm = document.getElementById('cpf_pm');
  if (cpf_pm) {
    if (cpf_pm.checked == true || pole_emploi_checkbox.checked == true) {
      if (document.getElementById('pm_shop_checkout2')) {
        document.getElementById('pm_shop_checkout2').innerText = 'Mobiliser mon CPF';
      }
      if (document.getElementById('pm_shop_checkout')) {
        document.getElementById('pm_shop_checkout').innerText = 'Mobiliser mon CPF';
      }
      if (cpf_pm.value == 'Formation pro') {
        document.getElementById('pm_shop_check').href = 'https://bit.ly/3uLde9W';
        document.getElementById('pm_shop_checkout').href = 'https://bit.ly/3uLde9W';
      }
      if (cpf_pm.value == 'Formation premium') {
        document.getElementById('pm_shop_check').href = 'https://bit.ly/3LJQLQP';
        document.getElementById('pm_shop_checkout').href = 'https://bit.ly/3LJQLQP';
      }
      // if (document.getElementById('promo_code')) {
      //   document.getElementById('promo_code').style.display = 'none';
      // }
      // if (document.getElementById('promo_button')) {
      //   document.getElementById('promo_button').style.display = 'none';
      // }
      // if (document.getElementById('promo_input')) {
      //   document.getElementById('promo_input').style.display = 'none';
      // }
      // if (document.getElementById('order_instalment')) {
      //   document.getElementById('order_instalment').style.display = 'none';
      //   document.getElementById('order_instalment_number').style.display =
      //     'none';
      //   document.getElementById('order_amount_to_pay').style.display = 'none';
      // }

      // hide instalment

      displayInstalmentPayment(); //hide instalment
      displayPromo(); //hide promo
      if (order_instalment) {
        order_instalment.style.display = 'none'; //hide instalment
        order_instalment_number.style.display = 'none';
      }
      if (order_amount_to_pay) {
        order_amount_to_pay.style.display = 'none';
      }
    }
  }

  if (document.getElementById('pm_shop_text')) {
    //Show CPF video and details
    document.getElementById('cpf-details').classList.remove('hide');
    document.getElementById('arrow-down').classList.remove('hide');

    document.getElementById('pm_shop_text').innerHTML = 'Mobiliser mon CPF';
    document.getElementById('pm_shop_check_text').innerHTML = 'Mobiliser mon CPF';
    document.getElementById('pm_shop_checkout_text').innerHTML = 'Mobiliser mon CPF';
  }
}

function onchangeTextButton1() {
  //hide cpf details when pole_emploi is checked
  hideAlertDate();
  if (document.getElementById('pole_emploi_checkbox')) {
    //hide poleEmploi details

    sendPoleEmploiState(pole_emploi_checkbox.checked);
    //send pole emploi checked
    hidePoleEmploiDetails();
  }

  if (document.getElementById('pm_shop_checkout')) {
    document.getElementById('pm_shop_checkout').innerText = 'Passer au paiement';
  }
  if (document.getElementById('pm_shop_checkout2')) {
    document.getElementById('pm_shop_checkout2').innerText = 'Passer au paiement';
  }
  if (document.getElementById('cpf-details')) {
    document.getElementById('cpf-details').classList.add('hide');
    if (document.getElementById('arrow-down')) {
      document.getElementById('arrow-down').classList.add('hide');
    }
  }
  // //show hide instalment
  displayInstalmentPayment(); //show instalment
  displayPromo(); //show promo
  // if (document.getElementById('promo_code')) {
  //   document.getElementById('promo_code').style.display = 'inline';
  // }
  // if (document.getElementById('promo_button')) {
  //   document.getElementById('promo_button').style.display = 'inline';
  // }

  // if (document.getElementById('promo_input')) {
  //   document.getElementById('promo_input').style.display = 'inline';
  // }
  // if (document.getElementById('order_instalment')) {
  //   document.getElementById('order_instalment').style.display = 'revert';
  //   document.getElementById('order_instalment_number').style.display = 'revert';
  //   document.getElementById('order_amount_to_pay').style.display = 'revert';
  //   document.getElementById('order_instalment').style.visibility = 'unset';
  //   document.getElementById('order_instalment_number').style.visibility =
  //     'unset';
  //   document.getElementById('order_amount_to_pay').style.visibility = 'unset';
  // }

  var stripe_pm = document.getElementById('stripe_pm');
  if (stripe_pm) {
    if (stripe_pm.checked == true) {
      document.getElementById('pm_shop_check').href = '/shop/checkout?express=1';

      document.getElementById('pm_shop_checkout').href = '/shop/checkout?express=1';
    }
  }

  if (document.getElementById('pm_shop_text')) {
    if (document.getElementById('cpf-details')) {
      document.getElementById('cpf-details').classList.add('hide');
      document.getElementById('arrow-down').classList.add('hide');
      if (document.getElementById('pm_shop_checkout')) {
        document.getElementById('pm_shop_checkout').innerHTML = 'Passer au paiement';
      }
      if (document.getElementById('pm_shop_checkout2')) {
        document.getElementById('pm_shop_checkout2').innerText = 'Passer au paiement';
      }
    }

    // if (document.getElementById('promo_code')) {
    //   document.getElementById('promo_code').style.display = 'inline';
    // } else {
    //   document.getElementById('promo_input').style.display = 'inline';
    //   document.getElementById('promo_button').style.display = 'inline';
    // }
    // if (document.getElementById('order_instalment')) {
    //   document.getElementById('order_instalment').style.display = 'visible';
    // }
    // instalment = document.getElementById('checkbox_instalment');
    // if (instalment) {
    //   if (instalment.checked == true) {
    //     document.getElementById('order_instalment_number').style.display =
    //       'visible';
    //     document.getElementById('order_amount_to_pay').style.display =
    //       'visible';
    //   }
    // }
  }
}
function show_coupon() {
  if (document.getElementById('promo_input')) {
    document.getElementById('promo_input').style.display = 'inline';
  }
  if (document.getElementById('promo_button')) {
    document.getElementById('promo_button').style.display = 'inline';
  }
}

// display promo - instalment

function showInstalment() {
  if (document.getElementById('order_instalment_number')) {
    document.getElementById('order_instalment_number').style.visibility = 'unset';
  }
  if (document.getElementById('order_amount_to_pay')) {
    document.getElementById('order_amount_to_pay').style.visibility = 'unset';
    document.getElementById('order_amount_to_pay').style.display = 'revert';
  }
}

function hideInstalment() {
  if (document.getElementById('order_instalment_number')) {
    document.getElementById('order_instalment_number').style.visibility = 'hidden';
  }
  if (document.getElementById('order_amount_to_pay')) {
    document.getElementById('order_amount_to_pay').style.visibility = 'hidden';
  }
}

function displayInstalmentPayment() {
  if (document.getElementById('order_instalment')) {
    var orderInstalment = document.getElementById('order_instalment');
    orderInstalment.style.visibility = 'unset';
    orderInstalment.style.display = 'revert';
    if (document.getElementById('checkbox_instalment')) {
      var instalment = document.getElementById('checkbox_instalment').checked;
      sendHttpRequest('POST', '/shop/payment/update_amount', {
        params: {
          instalment: instalment,
        },
      })
        .then((responseData) => {})
        .catch((err) => {});
      if (instalment) {
        showInstalment();
      } else {
        hideInstalment();
      }
    }
  }
}

function displayPromo() {
  if (document.getElementById('stripe_pm')) {
    if (document.getElementById('stripe_pm').checked) {
      showPromo();
    } else {
      hidePromo();
    }
  }
}
function showPromo() {
  if (document.getElementById('promo_code')) {
    //when promo button is shown we don't need to show promo_code
    if (document.getElementById('promo_button')) {
      if (document.getElementById('promo_button').style.display != 'none') {
        // document.getElementById('promo_code').style.display = 'none';
      } else {
        document.getElementById('promo_code').style.display = 'unset';
      }
    }
  }
  if (document.getElementById('promo_button')) {
    document.getElementById('promo_button').style.display = 'inline';
  }

  if (document.getElementById('promo_input')) {
    document.getElementById('promo_input').style.display = 'inline';
  }
}

function hidePromo() {
  if (document.getElementById('promo_code')) {
    document.getElementById('promo_code').style.display = 'none';
  }
  if (document.getElementById('promo_button')) {
    document.getElementById('promo_button').style.display = 'none';
  }
  if (document.getElementById('promo_input')) {
    document.getElementById('promo_input').style.display = 'none';
  }
}

//Disable both payment buttons
function disablePaymentButton() {
  document.getElementById('pm_shop_checkout').setAttribute('disabled', 'true');
  document.getElementById('pm_shop_checkout').classList.add('disabled');
  document.getElementById('pm_shop_checkout2').setAttribute('disabled', 'true');
  document.getElementById('pm_shop_checkout2').classList.add('disabled');
}
//Enable both payment buttons
function enablePaymentButton() {
  document.getElementById('pm_shop_checkout').setAttribute('disabled', 'false');
  document.getElementById('pm_shop_checkout').classList.remove('disabled');
  document.getElementById('pm_shop_checkout2').setAttribute('disabled', 'false');
  document.getElementById('pm_shop_checkout2').classList.remove('disabled');
}

// show a warning message for session > 4 months
function showAlertDate() {
  document.getElementById('error_choix_date_4').style.display = 'inline-block';
}
// hide the warning message for session > 4 months
function hideAlertDate() {
  document.getElementById('error_choix_date_4').style.display = 'none';
}

// This function substract 4 months from date session,
function sessionIsAccessible(prop) {
  hideAlertDate();
   if (window.location.href.includes('lourd')){
  return
  }
  // alert(new Date(prop));
  const toDay = new Date();
  const sessionDate = new Date(prop);
  console.log('sessionDate :', sessionDate);
  const months = monthDiff(toDay, sessionDate);

  //init
  let isAccessible = false;
  //if months == 4 check toDay's day is superior to session's day
  if (months == 4 && toDay.getFullYear() == sessionDate.getFullYear()) {
    console.log(
      sessionDate.getDate(),
      toDay.getDate(),
      sessionDate.getDate() - toDay.getDate() <= 0
    );
    sessionDate.getDate() - toDay.getDate() <= 0
      ? (isAccessible = true)
      : (isAccessible = false);
  } else if (months < 4) {
    isAccessible = true;
  }

  console.log('isAccessible :', isAccessible);
  if (!isAccessible) {
    showAlertDate();
    disablePaymentButton();
    setAvailableDate(sessionDate);
  } else {
    hideAlertDate();
    return;
  }
}
// Substract 2 dates and get months
function monthDiff(d1, d2) {
  var months;
  months = (d2.getFullYear() - d1.getFullYear()) * 12;
  months -= d1.getMonth();
  months += d2.getMonth();

  return months;
}

function formatDateEN(date) {
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
  });
}

function formatDateFR(date) {
  return date.toLocaleString('fr-FR', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
  });
}

function availableDate(sessionDate) {
  const month = sessionDate.getMonth();
  sessionDate.setMonth(sessionDate.getMonth() - 4);
  while (sessionDate.getMonth() === month) {
    sessionDate.setDate(sessionDate.getDate() - 1);
  }

  return formatDateFR(sessionDate);
}

function setAvailableDate(sessionDate) {
  if (document.getElementById('available-date')) {
    document.getElementById('available-date').innerHTML = availableDate(sessionDate);
  } else return;
}
