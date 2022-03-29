//required values to check necessary action
var cartIsEmpty = false;

var isSigned = '';
var rdvIsBooked = false;
const messages = {
  rdvIsBooked: `félicitations pour votre inscription, l'un de nos agents va vous contacter suite au rendez-vous réservé pour finaliser le financement de votre examen`,
  rdvIsnotbooked: `Veuillez réserver un créneau pour finaliser votre inscription a l'examen VTC afin d'accéder à la plateforme de formation`,
  isNotSigned: `Nous vous remercions pour votre confiance, votre paiement a été effectué avec succès! Vous pouvez maintenant finaliser votre inscription en signant votre contrat pour avoir accès à notre plateforme de formation.`,
  emptyCartNoContract: `Votre panier est vide, veuillez cliquer sur continuer pour ajouter votre formation.`,
};
var bolt_contract_uri = '/';
var btnAction;
function setPopup() {
  if (document.getElementById('cartIsEmpty')) {
    cartIsEmpty = document.getElementById('cartIsEmpty');
    //check if value exist
    if (cartIsEmpty) {
      if (document.getElementById('isSigned')) {
        isSigned = document.getElementById('isSigned').value;
      }
      if (document.getElementById('notifMessageBolt')) {
        notifMessage = document.getElementById('notifMessageBolt');
        //set the message
      }
      //contract is signed
      if (isSigned == 'True') {
        console.log(' is signed)');
        if (document.getElementById('rdvIsBooked')) {
          rdvIsBooked = document.getElementById('rdvIsBooked').value;
          // rdv is booked
          if (rdvIsBooked == 'True') {
            //set description inside popup
            notifMessage.textContent = messages['rdvIsBooked'];
            if (document.getElementById('btn-action')) {
              btnAction = document.getElementById('btn-action');
              btnAction.addEventListener('click', function () {
                // rdv is booked + contract is signed
                // redirection to my/home
                console.log('redirection...', 'myhome');
                window.location.href = '/my/home';
              });
            }
          } else {
            //rdv is not booked
            //open calendly to book appointment
            notifMessage.textContent = messages['rdvIsnotbooked'];
            if (document.getElementById('btn-action')) {
              btnAction = document.getElementById('btn-action');
              btnAction.innerText = 'Réserver un créneau';
              btnAction.addEventListener('click', function () {
                openCalendly();
              });
            }
          }
        }
      } else {
        console.log(document.getElementById('bolt_contract_uri').value);
        //contract is not signed
        //get uri to sign contract
        if (document.getElementById('bolt_contract_uri').value !== 'False') {
          bolt_contract_uri =
            document.getElementById('bolt_contract_uri').value;
          console.log(bolt_contract_uri);
          if (document.getElementById('btn-action')) {
            //set notification message to the right description
            notifMessage.textContent = messages['isNotSigned'];
            btnAction = document.getElementById('btn-action');
            //change button to 'signer mon contrat'
            btnAction.innerText = 'Signer mon contrat';
            btnAction.addEventListener('click', function () {
              //redirection to the uri
              console.log('redirection...', bolt_contract_uri);
              window.location.href = bolt_contract_uri;
            });
          }
        } else if (document.getElementById('btn-action')) {
          //set notification message to the right description
          notifMessage.textContent = messages['emptyCartNoContract'];
          btnAction = document.getElementById('btn-action');
          //change button to 'signer mon contrat'
          btnAction.innerText = 'continuer';
          btnAction.addEventListener('click', function () {
            //redirection to the uri
            console.log('redirection...', `/bolt#pricing`);
            window.location.href = `/bolt#pricing`;
          });
        }
      }

      //
    }
  }

  return;
}
//open popup
function openPopup() {
  document.getElementById('popupEmptyCart').style.display = 'flex';
}
//close popup
function closePopup() {
  document.getElementById('popupEmptyCart').style.display = 'none';
  window.location.href = '/my/home';
}
function openCalendly() {
  //Open Calendly on firing click action on calendly div
  if (document.querySelector('.calendly-badge-content')) {
    document.querySelector('.calendly-badge-content').click();
  } else {
    console.log('Calendly could not open');
  }
}

// Wait for the page to load, to set the popup btn action and message description
//
document.addEventListener('DOMContentLoaded', function () {
  setPopup();
  // receive user and user email address
  var user_name = '';
  var user_email = '';
  //check if values are available
  if (document.getElementById('user_name_connected')) {
    user_name = document.getElementById('user_name_connected').value;
  }
  if (document.getElementById('user_email_connected')) {
    user_email = document.getElementById('user_email_connected').value;
  }
  if (document.getElementById('isSigned')) {
    isSigned = document.getElementById('isSigned').value;
  }
  //Actions on signed contract

  //contract is signed
  if (isSigned == 'True') {
    //loggin info
    console.log('isSigned', isSigned);
    console.log('rdvIsBooked', rdvIsBooked);

    if (rdvIsBooked == 'False') {
      //set calendly if rdv is not booked
      setTimeout(function () {
        Calendly.initBadgeWidget({
          url: 'https://calendly.com/mcm-academy/examen-vtc-cma',
          prefill: {
            name: user_name,
            email: user_email,
          },
          text: "Inscription à l'examen VTC",
          color: '#1A1A1A',
          textColor: '#FFFFFF',
        });
      }, 1500);
    }
    openPopup();
  } else {
    //contract is not signed open popup
    if (document.getElementById('bolt_contract_uri')) {
      if (document.getElementById('bolt_contract_uri')) {
        openPopup();
      }
    }
  }
});
