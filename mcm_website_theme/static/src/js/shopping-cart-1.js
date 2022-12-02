var paymentMethod = 'all';
document.onreadystatechange = function () {
  if (document.readyState == "complete") {
    document.getElementById("cover-spin").remove();

    tourguide.start();

  }
}
document.addEventListener('DOMContentLoaded', function () {


  displayInstalmentPayment();
  var formation;
  if (document.getElementById('cpf_pm')) {
    formation = document.getElementById('cpf_pm').value;
  }
  // if (formation === 'Formation à distance VTC') {
  //   var urlVtc = 'https://www.youtube.com/embed/19BiYQVwZFs';
  //   document.getElementById('cpf_video').setAttribute('src', urlVtc);
  // } else {
  //   document
  //     .getElementById('cpf_video')
  //     .setAttribute('src', 'https://www.youtube.com/embed/vLIr9mckz8M');
  // }

  // onchangeTextButton1();

  //event listener on change sale conditions input
  // send post request to update sale conditions for the client on server
  // disable button if the checkboxcondition is false

  document.getElementById('checkbox_conditions').addEventListener('change', function () {
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
  //event on click on checkbox paiement installment
  if (document.getElementById('checkbox_instalment')) {
    document.getElementById('checkbox_instalment').addEventListener('click', function () {
      displayInstalmentPayment();
    });
  }

  // send departement_examen data if pack taxi 
  if (document.getElementById("departement_examen")) {
    const departement_examen = document.getElementById("departement_examen")
    departement_examen.addEventListener('change', function () {
      const departementId = departement_examen.options[departement_examen.selectedIndex].id
      console.log("departementId", departementId)
      if (departementId == "all") {
        sendExamDepartement('all')
      } else {
        sendExamDepartement(departementId)
      }
    })
  }

  // add on change event listener to deepartment department in case 
});


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

//
const addUserPlateform = () => {
  document.getElementById(
    'popupcontent'
  ).innerHTML = `<div style="text-align: -webkit-center;"><div class="spinner"></div></div>`;
  sendHttpRequest('POST', '/shop/adduser_plateform', {}).then((res) => {
    if (res) {
      if (res.result) {
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
                            <a onclick='window.open("${res.result.url}");return false;'> <button type="button" class="btn btn-shop shake" style="padding: 6px 34px;"> Continuer </button></a>
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
                                <a href="#"> <button type="button" class="btn btn-shop" onclick="closepopup()"  style="padding: 8px 29px;" > Fermer </button></a>

                            </div>
         `;
            }
            document.getElementById('popupcontent').innerHTML = `
                            <p style="margin-top: 12px;text-align: justify;">                              
                                 ${res.result.ajout}     
                            </p>
                            <div style="text-align:center">
                                <a href="#"> <button type="button" class="btn btn-shop"  onclick="closepopup()" style="padding: 8px 29px;" > Fermer </button></a>
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
                              <button type="button" class="btn btn-shop" id="non_renonce" style="padding: 7.5px 38.5px;" onclick="closepopup('/my/home')">Attendre 14 jours</button>
                                <button type="button" class="btn btn-shop shake" style="padding: 7.5px 38.5px;" onclick="renonce()" > Continuer </button>
                            </div>

         `;
          }
        }
      }
    }
  });
};


function onChangeCheckButton() {
  if (document.getElementById('options-date')) {
    if (
      document.getElementById('options-date').value === 'all' ||
      document.getElementById('region_examen').value === 'all'
    ) {

      document.getElementById('pm_shop_checkout').classList.add('disabled');

      document.getElementById('pm_shop_checkout2').classList.add('disabled');
    } else if (
      document.getElementById('options-date').value !== 'all' &&
      document.getElementById('region_examen').value !== 'all'
    ) {

      document.getElementById('pm_shop_checkout').classList.remove('disabled');

      document.getElementById('pm_shop_checkout2').classList.remove('disabled');
      document.getElementById('error_choix_date').style.display = 'none';
    }
  } else {

    document.getElementById('pm_shop_checkout').classList.add('disabled');

    document.getElementById('pm_shop_checkout2').classList.add('disabled');
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

  var stripe_pm = document.getElementById('stripe_pm');

  if (stripe_pm) {
    if (paymentMethod == "stripe_pm") {
      if (document.getElementById('from_bolt').value != 'False') {
        addcheckBoxBolt();
      } else {
        window.location.href = '/shop/checkout?express=1';
      }
    }
  }
  pole_emploi_pm = document.getElementById('pole_emploi_pm') ?? false;
  // if (pole_emploi_pm) {
  //   if (paymentMethod== "pole_emploi_pm") {
  //     window.location.href = '/new/ticket/pole_emploi';
  //   }
  // }
  var cpf_pm = document.getElementById('cpf_pm');
  // var state = 'accepted';
  var state = document.getElementById('state').value;

  if (cpf_pm) {
    var emploichecked = paymentMethod == "pole_emploi_pm" ? true : false;

    if (paymentMethod == "cpf_pm" || emploichecked == true) {
      if (cpf_pm.value == 'Formation à distance TAXI') {
        switch (true) {
          case state.includes('https://www.moncompteformation.gouv.fr/'):
            window.open(state, '_blank');

            break;
          case state == 'accepted':
            cpfAccepted();
            break;

          default:
            window.open('https://bit.ly/3GjhHn7', '_blank');

            break;
        }

        return;
      }
      if (cpf_pm.value == 'Formation à distance VMDTR') {
        switch (true) {
          case state.includes('https://www.moncompteformation.gouv.fr/'):
            window.open(state, '_blank');

            break;
          case state == 'accepted':
            cpfAccepted();
            break;

          default:
            window.open('https://bit.ly/3FCYXxK', '_blank');

            break;
        }

        return;
      }
      if (cpf_pm.value == 'Formation à distance VTC') {
        switch (true) {
          case state.includes('https://www.moncompteformation.gouv.fr/'):
            window.open(state, '_blank');

            break;
          case state == 'accepted':
            cpfAccepted();

            break;

          default:
            window.open('https://bit.ly/3452CaC', '_blank');

            break;
        }

        return;
      }
    }
  }
}
// Hide error when showing popup
function hideError_no_method() {
  if (document.getElementById('error_no_method').style.display == 'inline-block') document.getElementById('error_no_method').style.display = 'none';

}
// Scroll to error when we have a warning 
function scrollToError() {
  if (document.getElementById('options-date'))
    document.getElementById('options-date').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

//show popup function 
// responsable of showing the popup
// if all conditions are required to show the popup 
function showPopup() {
  let optionsDate = document.getElementById('options-date');
  if (optionsDate) optionsDate = optionsDate.value
  let cpfChecked = false;

  let departement;

  if (document.getElementById("region_examen")) {
    let region = document.getElementById("region_examen").value
    if (region != 'all') {
      document.getElementById('error_choix_region_examen').style.display = 'none';
      console.log("blingos")
    } else {
      document.getElementById('error_choix_region_examen').style.display = 'inline-block';
      scrollToError();
      return
    }

  }

  if (document.getElementById("departement_examen")) {
    console.log("1")
    departement = document.getElementById("departement_examen").value;
    if (departement != 'all' && departement != '') {
      document.getElementById('error_choix_departement').style.display = 'none';
      console.log("3")
    } else {
      document.getElementById('error_choix_departement').style.display = 'inline-block';
      scrollState = true;
      console.log("2")
      scrollToError()
      return
    }
  }
  if (optionsDate != 'all' && optionsDate != '') {
    document.getElementById('error_choix_date_popup').style.display = 'none';

  } else {
    document.getElementById('error_choix_date').style.display = 'inline-block';
    scrollToError();
    return
  }
  if (!document.getElementById('options-date')) {
    document.getElementById('error_no_date').style.display = 'block';
    scrollState = true;
    scrollToError()
    return;
  }
  if (!['pole_emploi_pm', 'stripe_pm', 'cpf_pm'].includes(paymentMethod)) {
    document.getElementById('error_no_method').style.display = 'inline-block';
    scrollState = true;
    scrollToError()
    return;
  }

  document.getElementById('error_no_method').style.display = 'none';
  document.getElementById('error_no_date').style.display = 'none';

  if (document.getElementById('cpf_pm')) {
    cpfChecked = paymentMethod == "cpf_pm" ? true : false;
  }
  var continueBtn = document.getElementById('continueBtn');
  var textbtn;
  var polechecked = false;
  if (document.getElementById('pole_emploi_pm')) {
    polechecked = paymentMethod == "pole_emploi_pm" ? true : false;

  }
  cpfChecked || polechecked
    ? (textbtn = 'Mobiliser mon CPF')
    : (textbtn = 'Je paye maintenant !');





  continueBtn.innerText = textbtn;
  window.location.href = '#popup1';
}

//When closing popup 
// recreate popup with initial content
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
                                        Je souhaite accéder à la formation dès maintenant sans attendre 14 jours. Je reconnais que MCM Academy
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
                       
                        

                        <div style="text-align:center">
                            <button type="button" class="btn btn-shop shake" id="continueBtn" onclick="verify_payment_method()">Continuer</button>
                        </div>`;
}

//hide pole emploie details
function hidePoleEmploiDetails() {
  if (document.getElementById('pole-emploi-details')) {
    document.getElementById('pole-emploi-details').classList.add('hide');
    // if (document.getElementById('arrow-down-pole-emploi')) {
    //   document.getElementById('arrow-down-pole-emploi').classList.add('hide');
    // }
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
    // if (document.getElementById('arrow-down')) {
    //   document.getElementById('arrow-down').classList.add('hide');
    // }
  }
}

//show pole emploie details
function showCpfDetails() {
  if (document.getElementById('cpf-details')) {
    document.getElementById('cpf-details').classList.remove('hide');
    // if (document.getElementById('arrow-down')) {
    //   document.getElementById('arrow-down').classList.remove('hide');
    // }
  }
}

//change button to mobiliser mon cpf or passer au paiment if cpf is checked or not
// according to that we show or hide cpf details and video

function onchangeTextButton() {
  //hide cpf details when pole_emploi is checked
  if (document.getElementById('pole_emploi_pm')) {
    if (paymentMethod == "pole_emploi_pm") {
      //send pole emploi checked = true
      //hide cpf details
      poleEmploieFixDisplay();
    } else if (paymentMethod == "cpf_pm") {
      //show cpf 
      showCpfDetails();
      //hide poleEmploi details
      hidePoleEmploiDetails();

      //send pole emploi checked
      sendPoleEmploiState(paymentMethod == "pole_emploi_pm");
    } else {

      //show cpf 
      hideCpfDetails
      //hide poleEmploi details
      hidePoleEmploiDetails();

      //send pole emploi checked
      sendPoleEmploiState(paymentMethod == "pole_emploi_pm");
    }
  }
  if (document.getElementById('pm_shop_checkout2')) {
    document.getElementById('pm_shop_checkout2').innerText = 'Mobiliser mon CPF';
  }
  if (document.getElementById('pm_shop_checkout')) {
    document.getElementById('pm_shop_checkout').innerText = 'Mobiliser mon CPF';
    displayInstalmentPayment(); //hide instalment
    displayPromo(); //hide promo

    order_instalment.style.display = 'none'; //hide instalment
    order_instalment_number.style.display = 'none';
    order_amount_to_pay.style.display = 'none';
  }
}
// Display when pole emploi is selected
function poleEmploieFixDisplay() {
  hideCpfDetails();
  //show pole emploi details
  showPoleEmploiDetails();
  sendPoleEmploiState(paymentMethod == "pole_emploi_pm");

}


// When carte bleu is selected
// all functions
function onchangeTextButton1() {
  if (document.getElementById('pole_emploi_pm')) {
    //hide poleEmploi details

    sendPoleEmploiState(false);
    //send pole emploi checked
    hidePoleEmploiDetails();
  }
  //onchange carte de credit
  if (document.getElementById('pm_shop_checkout')) {
    document.getElementById('pm_shop_checkout').innerText = 'Je paye maintenant !';
  }
  if (document.getElementById('pm_shop_checkout2')) {
    document.getElementById('pm_shop_checkout2').innerText = 'Je paye maintenant !';
  }
  hideCpfDetails()

  displayInstalmentPayment(); //show instalment
  displayPromo(); //show promo

  // if (document.getElementById('order_instalment')) {
  //   document.getElementById('order_instalment').style.display = 'revert';
  //   document.getElementById('order_instalment_number').style.display = 'revert';
  //   document.getElementById('order_amount_to_pay').style.display = 'revert';
  //   document.getElementById('order_instalment').style.visibility = 'unset';
  //   document.getElementById('order_instalment_number').style.visibility =
  //     'unset';
  //   document.getElementById('order_amount_to_pay').style.visibility = 'unset';
  // }
}

function renonce() {
  document.getElementById('popupcontent').innerHTML = `                 
                            <p id="notifMessage">
                            <div class="input checkbox" style="width:90%">
                                <input type="checkbox" id="checkbox_failures" style="white-space: nowrap;" class="text-xl-left border-0" t-att-checked="website_sale_order.failures" t-att-value="website_sale_order.failures">
                                    <label for="failures" style="display:inline">
                                        Je souhaite accéder à la formation dès maintenant sans attendre 14 jours. Je reconnais que MCM Academy
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
                             <button type="button" class="btn btn-shop" id="Précédent"  style="padding: 8px 29px;" onclick="cpfAccepted()">Précédent</button>
                             <button type="button" class="btn btn-shop shake" id="continueBtn" onclick="verify_payment_method()"style="padding: 8px 29px  ;   margin-left: 11px;">Continuer</button>
                          </div>
         `;
}

// display promo - instalment

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
  if (document.getElementById('promo_code')) {
    document.getElementById('promo_code').style.display =
      'none';
  }

}

function hideInstalment() {
  if (document.getElementById('order_instalment_number')) {
    document.getElementById('order_instalment_number').style.visibility = 'hidden';
  }
  if (document.getElementById('order_amount_to_pay')) {
    document.getElementById('order_amount_to_pay').style.visibility = 'hidden';
  }
  if (document.getElementById('promo_code')) {
    document.getElementById('promo_code').style.display =
      'unset';
  }
}
function selectPaymentInstallmentOption(instalment) {

  let select
  if (document.getElementById("financement")) {
    select = document.getElementById("financement");

  } else {
    return
  }
  index = document.getElementById("financement").selectedIndex
  if ([1, 2].indexOf(index) != -1) {
    if (instalment) {
      select.options[2].selected = 'selected'

    } else {
      select.options[1].selected = 'selected'
    }
  }
}
function displayInstalmentPayment() {
  if (document.getElementById('order_instalment')) {
    var orderInstalment = document.getElementById('order_instalment');
    orderInstalment.style.visibility = 'unset';
    orderInstalment.style.display = 'revert';
    if (document.getElementById('checkbox_instalment')) {
      var instalment = document.getElementById('checkbox_instalment').checked;
      selectPaymentInstallmentOption(instalment)
      if (instalment) {
        showInstalment();
        sendHttpRequest('POST', '/shop/payment/update_amount', {
          params: {
            instalment: true,
          },
        })
          .then((responseData) => { })
          .catch((err) => { });
      } else {
        hideInstalment();
        sendHttpRequest('POST', '/shop/payment/update_amount', {
          params: {
            instalment: false,
          },
        })
          .then((responseData) => { })
          .catch((err) => { });
      }
    }
  }
}

function displayPromo() {
  if (document.getElementById('stripe_pm')) {
    if (paymentMethod == "stripe_pm") {
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

// function show_coupon() {
//   if (document.getElementById('promo_input')) {
//     document.getElementById('promo_input').style.display = 'inline';
//   }
//   if (document.getElementById('promo_button')) {
//     document.getElementById('promo_button').style.display = 'inline';
//   }
// }
// function verify_checked() {
//   var x = document.getElementById('checkbox_instalment');
//   if (x) {
//     if (document.getElementById('checkbox_instalment').checked == true) {
//       document.getElementById('order_amount_to_pay').style.display = 'inline';
//       document.getElementById('order_instalment_number').style.display =
//         'inline';
//     } else {
//       document.getElementById('order_amount_to_pay').style.display = 'none';
//       document.getElementById('order_instalment_number').style.display = 'none';
//     }
//   }
// }


//boltPopupContent
const popContent = `
<b>
  Veuillez confirmer que vous détenez bien ces prérequis pour passer
  l'examen:</b
>

<div class="input checkbox mt24 mb24" style="width: 90%">
  <input
    type="checkbox"
    id="driver-licence"
    style="white-space: nowrap"
    class="text-xl-left border-0 "
  />
  <label for="driver-licence" style="display: inline">
    Vous avez 3 ans de permis ou plus.
  </label>
</div>
<div class="input checkbox mb24" style="width: 90%">
  <input
    type="checkbox"
    id="license_suspension"
    style="white-space: nowrap"
    class="text-xl-left border-0 
  />
  <label for="license_suspension" style="display: inline">
    Vous n'avez aucun retrait définitif du permis ces 10 dernières années.
  </label>
</div>
<div class="input checkbox mb24" style="width: 90%">
  <input
    type="checkbox"
    id="criminal_record"
    style="white-space: nowrap"
    class="text-xl-left border-0
  />
  <label for="criminal_record" style="display: inline">
    Vous avez un casier judiciaire vierge B2.
  </label>
</div>
<p
  id="error_choix_bolt"
  class="alert alert-warning"
  style="margin-left: 0%; margin-bottom: 13px; display: none"
>
  Si vous ne détenez pas ces 3 prérequis, vous ne pourrez pas vous inscrire à
  l'examen.
</p>
<div style="text-align: center">
  <button
    type="button"
    class="btn btn-shop"
    style="margin-top: 19px"
    id="continueBtn"
    onclick="paiementBolt()"
  >
    Je paye maintenant !
  </button>
</div>
`;

//BoltinitPopup
const popupContentinit = `<div class="input checkbox" style="width:90%">
                                <input type="checkbox" id="checkbox_failures" style="white-space: nowrap;" class="text-xl-left border-0" t-att-checked="website_sale_order.failures" t-att-value="website_sale_order.failures">
                                    <label for="failures" style="display:inline">
                                        Je souhaite accéder à la formation dès maintenant sans attendre 14 jours. Je
                                        reconnais que
                                     
                                        <span t-if="website_sale_order.company_id.id==1">MCM Academy</span>
                                        procédera à l'exécution immédiate de ma formation en ligne et à ce titre, je
                                        renonce expressément à exercer mon droit de rétractation conformément aux
                                        dispositions de
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
                        

                        <div style="text-align:center">
                            <button type="button" class="btn btn-shop" id="continueBtn" onclick="verify_payment_method()">Continuer
                            </button>
                        </div>`;


const addcheckBoxBolt = () => {
  var popupcontent = document.getElementById('popupcontent');
  popupcontent.innerHTML = popContent;
  var inputDriverLicence = document.getElementById('driver-licence');
  var inputLicenceSuspension = document.getElementById('license_suspension');
  var inputCriminalRecord = document.getElementById('criminal_record');

  inputDriverLicence.addEventListener('change', function () {
    update_driver_licence(inputDriverLicence.checked);
  });
  inputLicenceSuspension.addEventListener('change', function () {
    update_license_suspension(inputLicenceSuspension.checked);
  });
  inputCriminalRecord.addEventListener('change', function () {
    update_criminal_record(inputCriminalRecord.checked);
  });
};

function resetPopupBolt() {
  var popupcontent = document.getElementById('popupcontent');
  popupcontent.innerHTML = popupContentinit;
}

function checkInputBolt() {
  var inputDriverLicence = document.getElementById('driver-licence').checked;
  var inputLicenceSuspension = document.getElementById('license_suspension').checked;
  var inputCriminalRecord = document.getElementById('criminal_record').checked;
  if (inputDriverLicence && inputCriminalRecord & inputLicenceSuspension) {
    return true;
  } else return false;
}

function paiementBolt() {
  if (checkInputBolt()) {
    document.getElementById('error_choix_bolt').style.display = 'none';
    window.location.href = '#';
    window.location.href = '/shop/checkout?express=1';
    resetPopupBolt();
  } else {
    document.getElementById('error_choix_bolt').style.display = 'block';
  }
}

//Show departement for taxi 
function showDepartement() {
  if (document.getElementById("departement_examen")) {
    const departement = document.getElementById("departement_examen")
    if (departement.classList.contains("hide")) {
      departement.classList.remove("hide");
    }
    return
  }
}








//Get user partner Data information 
//HTTP REQUEST CALL
// const partnerInformation = async () => {
//   try {
//     // const res = await JSON.parse(sendHttpRequest('POST', '/get_data_user_connected', {}));
//     const res = await sendHttpRequest('POST', '/get_data_user_connected', {});
//     const partner = JSON.parse(res.result);
//     // console.log(partner.response);
//     // console.log(partner.response[0]);
//     return partner.response[0];
//   } catch (e) {
//     return 'error partnerInformation()';
//   }
// }

// const partnerInformation = async () => {
//   const data = await sendHttpRequest('POST', '/get_data_user_connected', {})
//     .then((res) => {

//       const partner = await JSON.parse(data.result);
//       console.log(partner)
//     })
//     .catch((err) => {
//       console.log(err);
//     });


//   }

// Base function mode de financement

function modeFinancement(mode, index) {
  paymentMethod = mode;
  console.log("indexxxx", index)
  switch (mode) {

    case "stripe_pm":
      onchangeTextButton1();
      update_cartebleu(true);
      hideError_no_method();
      if (index == 1) {
        checkPaiementInstalment(false)
      } else {
        checkPaiementInstalment(true)
      }

      break;
    case "cpf_pm":
      onchangeTextButton();

      update_cpf(true);
      showCpfDetails();
      fixDisplay();
      hideError_no_method();;


      break;
    case "pole_emploi_pm":
      onchangeTextButton();
      sendPoleEmploiState(true);

      fixDisplay()
      poleEmploieFixDisplay();
      hideError_no_method();
      break;
    case "pm_none":
      hideCpfDetails();
      hidePoleEmploiDetails();
      break;

    default:
      break;
  }
}


// fix display whene selecting pole emploi or cpf 
// paiement en plusieur fois 
// code promo 
function fixDisplay() {


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
    document.getElementById('order_instalment_number').style.visibility =
      'hidden';
    if (document.getElementById('order_instalment_number_order')) {
      document.getElementById('order_instalment_number_order').style.visibility =
        'hidden';
    }
    document.getElementById('order_amount_to_pay').style.display = 'none';
    if (document.getElementById('order_amount_to_pay_amount')) {
      document.getElementById('order_amount_to_pay_amount').style.display =
        'none';
    }

  }
}

// 


//animation
const sendData = (condition) => {
  sendHttpRequest('POST', '/shop/payment/update_condition', {
    params: {
      condition: condition,
    },
  })
    .then((responseData) => { })
    .catch((err) => { });
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

const update_driver_licence = (driver_licence) => {
  sendHttpRequest('POST', '/shop/update_driver_licence', {
    params: {
      driver_licence: driver_licence,
    },
  })
    .then((responseData) => { })
    .catch((err) => { });
};

const update_license_suspension = (license_suspension) => {
  sendHttpRequest('POST', '/shop/update_license_suspension', {
    params: {
      license_suspension: license_suspension,
    },
  })
    .then((responseData) => { })
    .catch((err) => { });
};

const update_criminal_record = (criminal_record) => {
  sendHttpRequest('POST', '/shop/update_criminal_record ', {
    params: {
      criminal_record: criminal_record,
    },
  })
    .then((responseData) => { })
    .catch((err) => { });
};

//emploie state value
// Création d'une fonction showpoleemploidetails pour afficher les détails de pole emploi et hidepoleemploidetails pour masquer les détails pole emploi.
// // Création d'une fonction sendpoleemploistate qui récupère l'état de radio button et envoyer cet état au backend avec un post request vers /shop/cart/update_pole_emploi  (checked : true ou false)
// // Cette méthode est utilise à chaque clic d'un radio button
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

const sendExamDepartement = (department_id) => {
  sendHttpRequest('POST', '/shop/cart/update_exam_department', {
    params: {
      department_id: department_id,
    },
  })
    .then((res) => {
      console.log(res);
    })
    .catch((err) => {
      console.log(err);
    });
};

// send carte_bleu selection
const update_cartebleu = (cartebleu) => {
  sendHttpRequest('POST', '/shop/payment/update_cartebleu',
    {
      params: {
        cartebleu: cartebleu,
      }
    })
    .then((res) => {
      console.log(res);
    })
    .catch((err) => {
      console.log(err);
    });
};

// send cpf selection
const update_cpf = (cpf) => {
  sendHttpRequest('POST', '/shop/payment/update_cpf',
    {
      params: { cpf: cpf }
    })
    .then((res) => {
      console.log(res);
    })
    .catch((err) => {
      console.log(err);
    });
};





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

function checkPaiementInstalment(check) {
  let checkbox = document.getElementById("checkbox_instalment")

  if (checkbox) {
    
    if (check != checkbox.checked) {
      checkbox.click();
      // Send installment when fix chekbox to the select options
      sendHttpRequest('POST', '/shop/payment/update_amount', {
        params: {
          instalment: checkbox.checked,
        },
      })
        .then((responseData) => { })
        .catch((err) => { });
      
    }
    else return
  }
  else return
  
}

