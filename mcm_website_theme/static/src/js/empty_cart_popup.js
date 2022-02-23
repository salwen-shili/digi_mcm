var cartIsEmpty = false;
var isSigned = false;
var rdvIsBooked = false;
const messages = {
  rdvIsBooked: `félicitations pour votre inscription, l'un de nos agents va vous contacter suite au rendez-vous réservé pour finaliser le financement de votre examen`,
  rdvIsnotbooked: `Veuillez réserver un créneau pour finaliser votre inscription a l'examen VTC afin d'accéder à la plateforme de formation`,
  isNotSigned: `Nous vous remercions pour votre confiance, votre paiement a été effectué avec succès! Vous pouvez maintenant finaliser votre inscription en signant votre contrat pour avoir accès à notre plateforme de formation.`,
};
var urlContract = '/';
var btnAction;
function setPopup() {
  if (document.getElementById('cartIsEmpty')) {
    cartIsEmpty = document.getElementById('cartIsEmpty');

    if (cartIsEmpty) {
      if (document.getElementById('isSigned')) {
        isSigned = document.getElementById('isSigned').value;
      }
      if (document.getElementById('notifMessageBolt')) {
        notifMessage = document.getElementById('notifMessageBolt');
        //set the message
      }
      if (isSigned) {
        if (document.getElementById('rdvIsBooked')) {
          rdvIsBooked = document.getElementById('rdvIsBooked').value;
          if (rdvIsBooked) {
            notifMessage.textContent = messages['rdvIsBooked'];
            if (document.getElementById('btn-action')) {
              btnAction = document.getElementById('btn-action');
              btnAction.addEventListener('click', function () {
                window.location.href = '/my/home';
              });
            }
          } else {
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
        if (document.getElementsByTagName('urlContract')) {
          urlContract = document.getElementsByTagName('urlContract');
          if (document.getElementById('btn-action')) {
            notifMessage.textContent = messages['isNotSigned'];
            btnAction = document.getElementById('btn-action');
            btnAction.innerText = 'Signer mon contrat';
            btnAction.addEventListener('click', function () {
              window.location.href = url;
            });
          }
        }
      }

      //
    }
  }

  return;
}

function openPopup() {
  document.getElementById('popupEmptyCart').style.display = 'flex';
}
function closePopup() {
  document.getElementById('popupEmptyCart').style.display = 'none';
  window.location.href = '/my/home';
}
function openCalendly() {
  document.querySelector('.calendly-badge-content').click();
}

//
document.addEventListener('DOMContentLoaded', function () {
  setPopup();
  var user_name = '';
  var user_email = '';
  if (document.getElementById('user_name_connected')) {
    user_name = document.getElementById('user_name_connected').value;
  }
  if (document.getElementById('user_email_connected')) {
    user_email = document.getElementById('user_email_connected').value;
  }
  if (isSigned) {
    console.log('isSigned', isSigned);
    console.log('rdvIsBooked', rdvIsBooked);

    if (!rdvIsBooked) {
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
    }
    openPopup();
  }
});
